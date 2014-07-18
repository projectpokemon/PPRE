"""

>>> from rawdb.elements.atom import BaseAtom
>>> class MyAtom(BaseAtom):
...     def __init__(self):
...         super(MyAtom, self).__init__()
...         self.int8('field1')
...         self.uint8('field2')
...         self.uint16('field3')
...
>>> atom = MyAtom()
>>> entry = atom('\xff\xff\x02\x01')
>>> entry.field1
-1
>>> entry.field3
258
>>> entry.field3 = 100
>>> str(entry)
'\xff\xff\x64\x00'

"""
from itertools import izip
import struct


class AtomicInstance(object):
    """

    Methods
    -------
    keys : list
        Get the valent attributes/keys of this atom
    """
    def __init__(self, atom, attrs):
        super(AtomicInstance, self).__setattr__('_attrs', attrs)
        super(AtomicInstance, self).__setattr__('_atom', atom)
        super(AtomicInstance, self).__setattr__('_frozen', False)

    def keys(self):
        return self._attrs.keys()

    def freeze(self):
        self._frozen = True
        return self

    def __getattr__(self, name):
        return self._attrs[name]

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setattr__(self, name, value):
        if self._frozen and name not in self._attrs:
            raise KeyError(name)
        self._attrs[name] = value

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __str__(self):
        return self._atom.pack(self._attrs)

    def __dict__(self):
        return self._attrs

    def __dir__(self):
        return self.keys()


class BaseAtom(object):
    """Base class for single element entries.

    This is used to read and build data formats.

    """
    atomic = AtomicInstance

    def __init__(self):
        self._fmt = []

    def __call__(self, data):
        # unpacked = struct.unpack(self.format_string(), data)
        # return self.atomic(self, dict(izip(self.keys(), unpacked)))
        return self.atomic(self, self.unpack(data)).freeze()

    def unpack(self, atom, data):
        data = data[:]
        unpacked = {}
        for entry in self.format_iterator():
            unpacked[entry[0]], data = self.unpack_one(entry[1], data)
        return unpacked

    def pack(self, atom, attrs):
        # unpacked = [attrs[name] for name in self.keys()]
        # return struct.pack(self.format_string(), *unpacked)
        packed = ''
        for entry in self.format_iterator():
            if not entry[1].strip('x'):
                packed += struct.pack(entry[1])
            else:
                packed += struct.pack(entry[1], attrs[entry[0]])
        return packed

    def keys(self):
        return [entry[0] for entry in self._fmt if entry[0]]

    def format_string(self):
        return ''.join([entry[1] for entry in self._fmt])

    def format_size(self):
        return struct.calcsize(self.format_string())

    def format_iterator(self):
        return self._fmt

    def unpack_one(self, formatter, data):
        """Unpack a single formatter from input data

        Parameters
        ----------
        formatter : string or function(data)
            format character or parser function
        data : string
            input data

        Returns
        -------
        value
            Value parsed
        data : string
            Remaining data
        """
        if hasattr(formatter, '__call__'):
            return formatter(data)
        elif not formatter.strip('x'):
            value = None
            consume = len(formatter)
        else:
            consume = struct.calcsize(formatter)
            value = struct.unpack(formatter, data[:consume])[0]
        return value, data[consume:]

    def int8(self, name):
        """Parse named field as int8

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'b')

    def uint8(self, name):
        """Parse named field as uint8

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'B')

    def int16(self, name):
        """Parse named field as int16

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'h')

    def uint16(self, name):
        """Parse named field as uint16

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'H')

    def int32(self, name):
        """Parse named field as int32

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'i')

    def uint32(self, name):
        """Parse named field as uint32

        Parameters
        ----------
        name : string
            Field name

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        return self.append_format(name, 'I')

    def padding(self, length):
        return self.append_format(None, 'x'*length)

    def array(self, format_entry, count=None, terminator=None):
        """Parse field array

        Parameters
        ----------
        name : string
            Name of field
        format_entry
            Formatter (result of self.int8(name), etc)
        count : int or None
            if not None, array stops growing at this size.
        terminator : int or None
            if not None, array stops when a value matching this shows up.
        """

        def array_func(data):
            total = 0
            arr = []
            while 1:
                if array_func.count is not None and total >= array_func.count:
                    break
                value, data = self.unpack_one(array_func.formatter, data)
                if array_func.terminator is not None \
                        and value == array_func.terminator:
                    break
                arr.append(value)
            return arr, data

        # Close values over this function and allow for mutations
        array_func.count = count
        array_func.terminator = terminator
        array_func.formatter = format_entry[1]
        format_entry[1] = array_func

    def append_format(self, name, formatter):
        """Add a new format entry

        Parameters
        ----------
        name : string
            Field name
        formatter : string or function(data)
            Describes how to format a section of data. If a string, this should
            be parsed using struct.pack

        Returns
        -------
        format_entry : tuple
            Format entry
        """
        format_entry = (name, formatter)
        self._fmt.append(format_entry)
        return format_entry
