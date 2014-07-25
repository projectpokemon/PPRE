
import struct

from rawdb.elements.atom.packer import Packer
from rawdb.elements.atom.data import DataConsumer


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

    def set_param(self, key, value):
        if key in self.valid_params:
            self.params[key] = value
        else:
            raise ValueError('%s is not a valid parameter' % key)

    def get_param(self, key, atomic):
        value = self.params[key]
        if hasattr(value, '__call__'):
            return value(atomic)
        return value

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


class ValenceMulti(ValenceFormatter):
    """Multiple SubValence container Valence

    For grouping multiple valences together

    Parameters
    ----------
    sub_valences : list(ValenceFormatter)
        List of contained ValenceFormatters
    """
    valid_params = ['sub_valences']

    def __init__(self, name, sub_valences):
        super(ValenceMulti, self).__init__(name)
        self.set_param('sub_valences', sub_valences)

    def format_iterator(self, atomic):
        return self.get_param('sub_valences', atomic)

    def unpack_one(self, atomic):
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

    def pack_one(self, atomic):
        return str(atomic)
