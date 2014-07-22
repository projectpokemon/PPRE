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
import abc
from itertools import izip
import struct


class AtomicInstance(object):
    """

    Methods
    -------
    keys : list
        Get the valent attributes/keys of this atom
    """
    def __init__(self, atom, consumer):
        super(AtomicInstance, self).__setattr__('_frozen', False)
        super(AtomicInstance, self).__setattr__('_attrs', {})
        super(AtomicInstance, self).__setattr__('_atom', atom)
        super(AtomicInstance, self).__setattr__('_data', consumer)

    def keys(self):
        return self._attrs.keys()

    @property
    def data(self):
        return self._data

    def freeze(self):
        super(AtomicInstance, self).__setattr__('_frozen', True)

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


class Packer(object):
    __metaclass__ = abc.ABCMeta

    def pack(self, attrs):
        packed = ''
        for entry in self.format_iterator(None):
            if not entry.ignore:
                packed += entry.pack_one(attrs[entry.name])
            else:
                packed += entry.pack_one(None)
        return packed


class DataConsumer(object):
    """
    Attributes
    ----------
    data : buffer
        Read-only data buffer
    offset : int
        Current offset of buffer
    """
    SEEK_RELATIVE = -1
    SEEK_ROOT = -2
    SEEK_TOP = 0

    def __init__(self, parent_or_buffer):
        try:
            self._data = parent_or_buffer.data
            self.parent = parent_or_buffer
            self.offset = self.base_offset = self.parent.offset
        except:
            self._data = parent_or_buffer[:]
            self.parent = None
            self.offset = self.base_offset = 0

    @property
    def data(self):
        """Read-only data"""
        return self._data

    @data.setter
    def data(self, value):
        raise TypeError('data is immutable')

    def consume(self, amount):
        self.offset += amount

    @property
    def exhausted(self):
        return self.offset-self.base_offset

    def __len__(self):
        return len(self.data)-self.offset

    def __getitem__(self, key):
        """Get a slice"""
        try:
            if not key.start:
                start = self.offset
            else:
                start = self.offset + key.start
            end = self.offset + key.stop
        except:
            raise TypeError('DataConsumer only accepts slice objects')
        data = self.data[start:end]
        self.offset = end
        return data

    def seek(self, offset, whence=SEEK_RELATIVE):
        if whence == self.SEEK_RELATIVE:
            self.offset += offset
        elif whence == self.SEEK_ROOT:
            self.offset = 0 + offset
        else:
            target = self
            for i in xrange(whence):
                target = target.parent
            self.offset = target.base_offset + offset


class ValenceFormatter(Packer):
    """Formatter that extends struct's functionality

    Methods
    -------
    pack_one : function
        Takes a value and formats it to a string
    unpack_one : function
        Takes a string and pulls out the value and remaining string from it.
        If value is None, it should not be considered.

    Attributes
    ----------
    format_char : string
        Struct format string for field
    count : int
        Array length for field
    terminator : int
        Array terminator value
    subatomic : type
        AtomicInstance type for creating subatoms
    ignore : bool
        If set to True, do not add to Atomic attributes (ex, padding)
    """
    def __init__(self, name, format_char=None, array_item=None,
                 sub_formats=None):
        self.name = name
        self.format_char = format_char
        self.array_item = array_item
        self.sub_formats = sub_formats
        if format_char is not None:
            self.unpack_one = self.unpack_char
            self.pack_one = self.pack_char
        elif array_item is not None:
            self.formatter = array_item
            self.unpack_one = self.unpack_array
            self.pack_one = self.pack_array
        elif sub_formats is not None:
            self.unpack_one = self.unpack_multi
            self.pack_one = self.pack_multi
        self.ignore = False

    def copy(self):
        kwargs = dict(name=self.name, format_char=self.format_char)
        if self.array_item:
            kwargs['array_item'] = self.array_item.copy()
        if self.sub_formats:
            kwargs['sub_formats'] = [entry.copy()
                                     for entry in self.sub_formats]
        new_formatter = ValenceFormatter(**kwargs)
        for attr, value in self.__dict__.items():
            if attr in ['subatomic'] or not hasattr(value, '__call__'):
                setattr(new_formatter, attr, value)
        return new_formatter

    def format_iterator(self, atomic):
        return self.sub_formats

    def unpack_char(self, atomic):
        if not self.format_char.strip('x'):
            value = None
            consume = len(self.format_char)
            atomic.data.consume(consume)
        else:
            consume = struct.calcsize(self.format_char)
            value = struct.unpack(self.format_char, atomic.data[:consume])[0]
        return value

    def pack_char(self, value):
        if not self.format_char.strip('x'):
            data = struct.pack(self.format_char)
        else:
            data = struct.pack(self.format_char, value)
        return data

    def unpack_array(self, atomic):
        total = 0
        arr = []
        while 1:
            if self.count is not None and total >= self.count:
                break
            value = self.formatter.unpack_one(atomic)
            if self.terminator is not None \
                    and value == self.terminator:
                break
            arr.append(value)
            total += 1
        return arr

    def pack_array(self, arr):
        data = ''
        for value in arr:
            data += self.formatter.pack_one(value)
        if self.terminator is not None:
            data += self.formatter.pack_one(self.terminator)
        # TODO: count validation
        return data

    def unpack_multi(self, atomic):
        data = DataConsumer(atomic.data)
        unpacked = {}
        subatomic = self.subatomic(self, data)
        for entry in self.format_iterator(subatomic):
            value = entry.unpack_one(subatomic)
            if not entry.ignore:
                subatomic[entry.name] = value
        subatomic.freeze()
        atomic.data.consume(subatomic.data.exhausted)
        return subatomic

    def pack_multi(self, atomic):
        return str(atomic)


class BaseAtom(Packer):
    """Base class for single element entries.

    This is used to read and build data formats.

    """
    atomic = AtomicInstance
    subatomic = AtomicInstance

    def __init__(self):
        self._fmt = []
        self._subfmts = []

    def __call__(self, data):
        if self._subfmts:
            raise RuntimeError('Subatoms have not returned fully')
        data = DataConsumer(data)
        atomic = self.atomic(self, data)
        unpacked = {}
        for entry in self.format_iterator(atomic):
            value = entry.unpack_one(atomic)
            if not entry.ignore:
                atomic[entry.name] = value
        atomic.freeze()
        return atomic

    def keys(self):
        return [entry.name for entry in self._fmt if entry.name]

    def format_iterator(self, atomic):
        return self._fmt

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
        return self.append_format(ValenceFormatter(name, 'b'))

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
        return self.append_format(ValenceFormatter(name, 'B'))

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
        return self.append_format(ValenceFormatter(name, 'h'))

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
        return self.append_format(ValenceFormatter(name, 'H'))

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
        return self.append_format(ValenceFormatter(name, 'i'))

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
        return self.append_format(ValenceFormatter(name, 'I'))

    def string(self, name, count=0):
        return self.append_format(ValenceFormatter(name, '%ds' % count))

    def padding(self, length):
        entry = ValenceFormatter(None, 'x'*length)
        entry.ignore = True
        return self.append_format(entry)

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
        return self.replace_format(format_entry, new_entry, pop=False)

    def sub_push(self, name):
        self._subfmts.append((name, self._fmt))
        self._fmt = []

    def sub_pop(self):
        sub_fmt = self._fmt
        name, self._fmt = self._subfmts.pop()
        format_entry = ValenceFormatter(name, sub_formats=sub_fmt)
        format_entry.subatomic = self.subatomic
        return self.append_format(format_entry)

    def append_format(self, formatter):
        """Add a new format entry

        Parameters
        ----------
        name : string
            Field name
        formatter : ValenceFormatter
            Describes how to format a section of data.

        Returns
        -------
        formatter : ValenceFormatter
            Format entry
        """
        self._fmt.append(formatter)
        return formatter

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

    def pop_format(self, index=-1):
        """Pops off the last (or specified) formatter

        Paramters
        ---------
        index : int, optional
            Index to remove

        Returns
        -------
        formatter : ValenceFormatter
            Popped formatter
        """
        return self._fmt.pop(index)
