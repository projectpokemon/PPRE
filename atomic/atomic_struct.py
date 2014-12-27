"""AtomicStruct version 2 Interface

AtomicStruct defines a structure for parsing raw data efficiently. The
substructures are compiled into a C-type equivalent.

"""
import ctypes


class AtomicError(RuntimeError):
    pass


class AtomicStruct(object):
    def __init__(self, name=None):
        self._fields = []
        self._field_pos = 0
        self.type = None
        self.data = None
        if name is None:
            self.name = self.__class__.__name__

    def _add(self, name, type_):
        if self.data is not None:
            raise AtomicError('Frozen Atoms cannot be modified')
        self._fields.insert(self._field_pos, (name, type_))
        self._field_pos += 1
        return (name, type_)

    def uint16(self, name):
        return self._add(ctypes.uint16(name))

    def embed(self, name, type_callable):
        return self._add(name, type_callable())

    def array(self, name, type_callable, length=1):
        return self._add(name, type_callable() * length)

    def struct(self):
        return self.type

    def __call__(self):
        return self.type

    def freeze(self):
        self.type = type(self.name, (ctypes.Structure),
                         dict(_fields_=self._fields))
        self.data = self()
