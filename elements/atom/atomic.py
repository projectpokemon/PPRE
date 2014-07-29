
from rawdb.elements.atom.data import DataBuilder


class AtomicInstance(object):
    """

    Methods
    -------
    keys : list
        Get the valent attributes/keys of this atom
    """
    def __init__(self, atom, consumer):
        super(AtomicInstance, self).__setattr__('_frozen', False)
        super(AtomicInstance, self).__setattr__('_attrs', {})
        super(AtomicInstance, self).__setattr__('_atom', atom)
        super(AtomicInstance, self).__setattr__('_data', consumer)

    def keys(self):
        return self._attrs.keys()

    @property
    def data(self):
        return self._data

    def freeze(self):
        super(AtomicInstance, self).__setattr__('_frozen', True)

    def __getattr__(self, name):
        return self._attrs[name]

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setattr__(self, name, value):
        if self._frozen and name not in self._attrs:
            raise KeyError(name)
        self._attrs[name] = value

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __str__(self):
        consumer = self._data
        data = DataBuilder()
        super(AtomicInstance, self).__setattr__('_data', data)
        value = str(self._atom.pack(self, data))
        super(AtomicInstance, self).__setattr__('_data', consumer)
        return value

    def __dict__(self):
        return self._attrs

    def __dir__(self):
        return self.keys()
