
from __future__ import absolute_import

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
