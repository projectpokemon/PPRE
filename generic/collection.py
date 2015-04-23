
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

    def append(self, obj):
        if not self.resizable:
            raise ValueError('This SizedCollection is not resizable')
        length = self.entries._length_
        old_entries = self.entries
        self._data = None  # HACK: Deletes all contents and thaws definition
        self.remove('entries')
        self._add('entries', old_entries._type_*(length+1))
        self.restrict('entries')
        self.freeze()
        ctypes.memmove(self.entries, old_entries, ctypes.sizeof(old_entries))
        self[length] = obj

    def base_struct(self, name):
        raise TypeError('Cannot embed resizable data structure')

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
