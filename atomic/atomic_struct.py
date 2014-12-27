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
        self._pack = 32
        self._anonymous = []
        self._type = None
        self._data = None
        if name is None:
            self.name = self.__class__.__name__

    def _add(self, name, type_):
        if self._data is not None:
            raise AtomicError('Frozen Atoms cannot be modified')
        self._fields.insert(self._field_pos, (name, type_))
        self._field_pos += 1
        return (name, type_)

    def uint16(self, name):
        return self._add(name, ctypes.c_uint16)

    def embed(self, name, type_callable, base_obj=None):
        base_obj = base_obj or self
        self._anonymous.append(name)
        return self._add(name, type_callable())

    def array(self, name, type_callable, base_obj=None, length=1):
        base_obj = base_obj or self
        return self._add(name, type_callable() * length)

    def struct(self, name, type_callable, base_obj=None):
        base_obj = base_obj or self
        return self._add(name, type_callable())

    def base_struct(self, name):
        return (name, self._type)

    def __call__(self):
        return self._type

    def freeze(self):
        self._type = type(self.name, (ctypes.Structure),
                          dict(_fields_=self._fields, _pack_=self._pack,
                               _anonymous_=tuple(self._anonymous)))
        self._data = self()
