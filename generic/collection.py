
from __future__ import absolute_import

import ctypes

from generic import Editable


class Collection2d(Editable):
    def define(self, entry, width, height):
        self.width = width
        self.height = height
        self.array('entries', entry, length=width*height)

    def __getitem__(self, key):
        try:
            idx = key[1]*self.width+key[0]
        except (IndexError, TypeError):
            raise KeyError('2d Collection expects a two-tuple index')
        return self.entries[idx]

    def __setitem__(self, key, value):
        try:
            idx = key[1]*self.width+key[0]
        except (IndexError, TypeError):
            raise KeyError('2d Collection expects a two-tuple index')
        self.entries[idx] = value


class SizedCollection(Editable):
    def define(self, entry, length, resizable=True):
        self.resizable = resizable
        self.array('entries', entry, length=length, max_length=0xFFFFFFF)

    def resize(self, length):
        if not self.resizable:
            raise ValueError('This SizedCollection is not resizable')
        old_length = self.entries._length_
        old_entries = self.entries
        new_type = old_entries._type_*(length)
        self._data = None  # HACK: Deletes all contents and thaws definition
        self.remove('entries')
        self._add('entries', new_type)
        self.restrict('entries')
        self.freeze()
        if old_length < length:
            size = ctypes.sizeof(old_entries)
        else:
            size = ctypes.sizeof(self.entries)
        ctypes.memmove(self.entries, old_entries, size)

    def append(self, obj):
        length = self.entries._length_
        self.resize(length+1)
        self[length] = obj

    def base_struct(self, name):
        if self.resizable:
            raise TypeError('Cannot embed resizable data structure')
        return Editable.base_struct(self, name)

    def __getitem__(self, key):
        return self.entries[key]

    def __setitem__(self, key, value):
        """Accepts assignment from similar entry objects as well as dicts
        containing object properties

        See Also
        --------
        Editable.from_dict
        """
        try:
            value_size = ctypes.sizeof(value)
        except TypeError:
            self.entries[key].from_dict(value)
        else:
            entry_size = ctypes.sizeof(self.entries[key])
            if value_size != entry_size:
                raise ValueError('Incorrect type. Expected {0}'
                                 .format(self.entries[key]._type_))
            ctypes.memmove(ctypes.addressof(self.entries[key]),
                           ctypes.addressof(value), entry_size)

    def __len__(self):
        return len(self.entries)

    def __iter__(self):
        return iter(self.entries)
