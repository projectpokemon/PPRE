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


class ValenceFormatter(object):
    """Formatter that extends struct's functionality

    Methods
    -------
    pack_one : function
        Takes a value and formats it to a string
    unpack_one : function
        Takes a string and pulls out the value and remaining string from it

    Attributes
    ----------
    format_char : string
        Struct format string for field
    count : int
        Array length for field
    terminator : int
        Array terminator value
    """
    def __init__(self, name, format_char=None, array_item=None):
        self.name = name
        if format_char is not None:
            self.format_char = format_char
            self.unpack_one = self.unpack_char
            self.pack_one = self.pack_char
        elif array_item is not None:
            self.formatter = array_item
            self.unpack_one = self.unpack_array
            # self.pack_one = self.pack_array

    def unpack_char(self, data):
        if not self.format_char.strip('x'):
            value = None
            consume = len(self.format_char)
        else:
            consume = struct.calcsize(self.format_char)
            value = struct.unpack(self.format_char, data[:consume])[0]
        return value, data[consume:]

    def pack_char(self, value):
        if not self.format_char.strip('x'):
            data = struct.pack(self.format_char)
        else:
            data = struct.pack(self.format_char, value)
        return data

    def unpack_array(self, data):
        total = 0
        arr = []
        while 1:
            if self.count is not None and total >= self.count:
                break
            value, data = self.formatter.unpack_one(data)
            if self.terminator is not None \
                    and value == self.terminator:
                break
            arr.append(value)
        return arr, data


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

    def unpack(self, data):
        data = data[:]
        unpacked = {}
        for entry in self.format_iterator():
            unpacked[entry.name], data = entry.unpack_one(data)
        return unpacked

    def pack(self, attrs):
        packed = ''
        for entry in self.format_iterator():
            packed += entry.pack_one(attrs[entry.name])
        return packed

    def keys(self):
        return [entry.name for entry in self._fmt if entry.name]

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

        new_entry = ValenceFormatter(format_entry.name,
                                     array_item=format_entry)
        new_entry.count = count
        new_entry.terminator = terminator
        return self.replace_format(format_entry, new_entry)

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
        format_entry : ValenceFormatter
            Format entry
        """
        format_entry = ValenceFormatter(name, format_char=formatter)
        self._fmt.append(format_entry)
        return format_entry

    def replace_format(self, old_ref, new_entry, pop=True):
        """Replace an old format entry with a new one

        Parameters
        ----------
        old_ref : string or ValenceFormatter
            Item to replace
        new_entry : ValenceFormatter
            New format entry
        pop : bool
            If pop is True, remove new_entry from format list
        """
        if pop:
            self.remove_format(new_entry)
        if isinstance(old_ref, ValenceFormatter):
            index = self._fmt.index(old_ref)
            self._fmt[index] = new_entry
        else:
            self._fmt = [new_entry if fmt.name == old_ref else fmt
                         for fmt in self._fmt]
        return new_entry

    def remove_format(self, old_ref):
        """Remove a format entry by reference

        Parameters
        ----------
        old_ref : string or ValenceFormatter
            Reference to item or item's name to remove
        """
        if isinstance(old_ref, ValenceFormatter):
            self._fmt.remove(old_ref)
        else:
            self._fmt = [fmt for fmt in self._fmt if fmt.name != old_ref]
