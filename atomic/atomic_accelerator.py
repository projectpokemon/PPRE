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
    @staticmethod
    def initialize(atomic, name=None):
        AtomicStruct.__init__(atomic, name)
        try:
            entry = accelerated_cache[atomic._name]
        except KeyError:
            pass
        else:
            for attr in entry.__slots__:
                setattr(atomic, attr, getattr(entry, attr))
            atomic._data = atomic._type()
            atomic.set_defaults()

    @staticmethod
    def freeze(atomic):
        if atomic._data is not None:
            return
        AtomicStruct.freeze(atomic)
        entry = accelerated_cache[atomic._name] = AtomicCacheEntry()
        for attr in entry.__slots__:
            setattr(entry, attr, getattr(atomic, attr))
