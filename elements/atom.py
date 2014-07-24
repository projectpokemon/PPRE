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
    count : int or function(atomic)
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
        """Unpacks the format_char string from atomic.data

        If self.format_char is a function, this will be called with atomic as
        the first argument to generate the format string
        """
        try:
            format_char = self.format_char(atomic)
        except:
            format_char = self.format_char
        if not format_char.strip('x'):
            value = None
            consume = len(format_char)
            atomic.data.consume(consume)
        else:
            consume = struct.calcsize(format_char)
            value = struct.unpack(format_char, atomic.data[:consume])[0]
        return value

    def pack_char(self, value):
        # TODO: format_char as function
        if not self.format_char.strip('x'):
            data = struct.pack(self.format_char)
        else:
            data = struct.pack(self.format_char, value)
        return data

    def unpack_array(self, atomic):
        total = 0
        arr = []
        try:
            count = self.count(atomic)
        except:
            count = self.count
        try:
            terminator = self.terminator(atomic)
        except:
            terminator = self.terminator
        while 1:
            if count is not None and total >= count:
                break
            value = self.formatter.unpack_one(atomic)
            if terminator is not None \
                    and value == terminator:
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
