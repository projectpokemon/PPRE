"""AtomicStruct version 2 Interface

AtomicStruct defines a structure for parsing raw data efficiently. The
substructures are compiled into a C-type equivalent.

"""
import ctypes


class AtomicError(RuntimeError):
    pass


class AtomicContext(object):
    def __init__(self, atomic, key):
        self.atomic = atomic
        self.key = key

    def __enter__(self, value=True):
        self.old_value = self.atomic.ctx[self.key]
        self.atomic.ctx[self.key] = value

    def __exit__(self, type_, value_, traceback):
        self.atomic.ctx[self.key] = self.old_value


class AtomicStruct(object):
    def __init__(self, name=None):
        self._fields = []
        self._pack = 32
        self._anonymous = []
        self._type = None
        self._data = None
        self.context = {
            'field_pos': 0,
            'simulate': False
        }
        if name is None:
            self.name = self.__class__.__name__

    def _add(self, name, type_):
        if not self.context['simulate']:
            if self._data is not None:
                raise AtomicError('Frozen Atoms cannot be modified')
            self._fields.insert(self.context['field_pos'], (name, type_))
            self.context['field_pos'] += 1
        return (name, type_)

    def simulate(self):
        return AtomicContext(self, 'simulate')

    def uint16(self, name):
        return self._add(name, ctypes.c_uint16)

    def embed(self, name, type_callable, base_obj=None):
        self._anonymous.append(name)
        with (base_obj or self).simulate():
            return self._add(name, type_callable())

    def array(self, name, type_callable, base_obj=None, length=1):
        with (base_obj or self).simulate():
            return self._add(name, type_callable() * length)

    def struct(self, name, type_callable, base_obj=None):
        with (base_obj or self).simulate():
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
