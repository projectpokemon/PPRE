"""AtomicStruct version 2 Interface

AtomicStruct defines a structure for parsing raw data efficiently. The
substructures are compiled into a C-type equivalent.

"""
import ctypes

from util import BinaryIO


class AtomicError(RuntimeError):
    pass


class AtomicExhaustionError(AtomicError):
    pass


class AtomicContext(object):
    def __init__(self, atomic, key, value=True, rel=False):
        self.atomic = atomic
        self.key = key
        self.rel = rel
        self.value = value

    def __enter__(self):
        self.old_value = self.atomic.context[self.key]
        self.atomic.context[self.key] = self.value

    def __exit__(self, type_, value_, traceback):
        if self.rel and self.old_value > self.value:
            self.atomic.context[self.key] += self.old_value - self.value
        else:
            self.atomic.context[self.key] = self.old_value


class AtomicStruct(object):
    alignment = 32

    def __init__(self, name=None):
        self._fields = []
        self._anonymous = []
        self._type = None
        self._data = None
        self._defaults = {}
        self.context = {
            'field_pos': 0,
            'simulate': False
        }
        if name is None:
            self.name = self.__class__.__name__

    def _add(self, name, type_, **kwargs):
        if not self.context['simulate']:
            if self._data is not None:
                raise AtomicError('Frozen Atoms cannot be modified')
            if name == '_':
                raise AtomicError('Subtype is not being simulated when '
                                  'fetched. base_obj={0}'.format(self))
            if 'width' in kwargs:
                field = (name, type_, kwargs['width'])
            else:
                field = (name, type_)
            self._fields.insert(self.context['field_pos'], field)
            self.context['field_pos'] += 1
            if 'default' in kwargs:
                self._defaults[name] = kwargs['default']
        return (name, type_)

    def simulate(self):
        return AtomicContext(self, 'simulate')

    def find(self, name):
        """Get the field position of a field by name"""
        for idx, field in enumerate(self._fields):
            if field[0] == name:
                return idx
        raise IndexError('Could not find {0}'.format(name))

    def after(self, name=None):
        if name is None:
            pos = 0
        else:
            pos = self.find(name)+1
        return AtomicContext(self, 'field_pos', pos, rel=True)

    def uint8(self, name, **kwargs):
        return self._add(name, ctypes.c_uint8, **kwargs)

    def int8(self, name, **kwargs):
        return self._add(name, ctypes.c_int8, **kwargs)

    def uint16(self, name, **kwargs):
        return self._add(name, ctypes.c_uint16, **kwargs)

    def int16(self, name, **kwargs):
        return self._add(name, ctypes.c_int16, **kwargs)

    def uint32(self, name, **kwargs):
        return self._add(name, ctypes.c_uint32, **kwargs)

    def int32(self, name, **kwargs):
        return self._add(name, ctypes.c_int32, **kwargs)

    def char(self, name, **kwargs):
        return self._add(name, ctypes.c_char, **kwargs)

    def string(self, name, length=1, **kwargs):
        return self.array(name, self.char, self, length=length)

    def get_type(self, type_callable, base_obj=None):
        with (base_obj or self).simulate():
            return type_callable('_')[1]

    def embed(self, name, type_callable, base_obj=None):
        self._anonymous.append(name)
        return self._add(name, self.get_type(type_callable, base_obj))

    def array(self, name, type_callable, base_obj=None, length=1):
        return self._add(name,
                         self.get_type(type_callable, base_obj) * length)

    def struct(self, name, type_callable, base_obj=None):
        return self._add(name, self.get_type(type_callable, base_obj))

    def base_struct(self, name):
        return (name, self._type)

    def __call__(self):
        return self._type

    def __len__(self):
        return ctypes.sizeof(self._data)

    def freeze(self):
        self._type = type('struct_'+self.name, (ctypes.Structure, ),
                          dict(_fields_=self._fields, _pack_=self.alignment,
                               _anonymous_=tuple(self._anonymous)))
        self._data = self._type()
        for key, value in self._defaults.iteritems():
            setattr(self._data, key, value)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        amount = len(self)
        data = reader.read(amount)
        self._data.from_buffer_copy(data)

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        amount = len(self)
        writer.write(ctypes.string_at(ctypes.addressof(self._data),
                                      size=amount))
        return writer
