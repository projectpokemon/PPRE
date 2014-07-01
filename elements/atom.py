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
    def __init__(self, atom, attrs):
        super(AtomicInstance, self).__setattr__('_attrs', attrs)
        super(AtomicInstance, self).__setattr__('_atom', atom)

    def __getattr__(self, name):
        return self._attrs[name]

    def __setattr__(self, name, value):
        if name not in self._attrs:
            raise KeyError(name)
        self._attrs[name] = value

    def __str__(self):
        return self._atom.pack(self._attrs)

    def __dict__(self):
        return self._attrs

    def __dir__(self):
        return self._attrs.keys()


class BaseAtom(object):
    """Base class for single element entries.

    This is used to read and build data formats.

    """
    def __init__(self):
        self._fmt = []

    def __call__(self, data):
        unpacked = struct.unpack(self.format_string(), data)
        return AtomicInstance(self, dict(izip(self.keys(), unpacked)))

    def pack(self, attrs):
        unpacked = [attrs[name] for name in self.keys()]
        return struct.pack(self.format_string(), *unpacked)

    def keys(self):
        return [entry[0] for entry in self._fmt if entry[0]]

    def format_string(self):
        return ''.join([entry[1] for entry in self._fmt])

    def int8(self, name):
        self.append_format(name, 'b')

    def uint8(self, name):
        self.append_format(name, 'B')

    def int16(self, name):
        self.append_format(name, 'h')

    def uint16(self, name):
        self.append_format(name, 'H')

    def int32(self, name):
        self.append_format(name, 'i')

    def uint32(self, name):
        self.append_format(name, 'I')

    def padding(self, length):
        self.append_format(None, 'x'*length)

    def append_format(self, name, fmt):
        self._fmt += [(name, fmt)]
