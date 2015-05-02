"""AtomicStruct version 2 Accelerated Interface

AcceleratedAtomicStructs allow for constant AtomicStruct definitions that
use the same base type across all instances so that they do not need
to be recompiled.

"""

from atomic.atomic_struct import AtomicStruct


accelerated_cache = {}


class AtomicCacheEntry(object):
    __slots__ = [
        '_pack_',
        '_anonymous_',
        '_fields_',
        '_defaults',
        '_type'
    ]


class AcceleratedAtomicStruct(AtomicStruct):
    """Accelerated Atomic Struct interface

    To use, subclass AtomicStruct and call this class's __init__ and freeze
    instead of using AtomicStruct's supered methods

    """
    def __init__(self, name=None):
        AtomicStruct.__init__(self, name)
        try:
            entry = accelerated_cache[self._name]
        except KeyError:
            pass
        else:
            for attr in entry.__slots__:
                setattr(self, attr, getattr(entry, attr))
            self._data = self._type()
            self.set_defaults()

    def freeze(self):
        if self._data is not None:
            return
        AtomicStruct.freeze(self)
        entry = accelerated_cache[self._name] = AtomicCacheEntry()
        for attr in entry.__slots__:
            setattr(entry, attr, getattr(self, attr))
