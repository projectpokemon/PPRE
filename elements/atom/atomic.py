
from rawdb.elements.atom.data import DataBuilder
from rawdb.util import code


class AtomicInstance(object):
    """

    Methods
    -------
    keys : list
        Get the valent attributes/keys of this atom
    """
    def __init__(self, packer, consumer, parent=None, namespace=None):
        super(AtomicInstance, self).__setattr__('_frozen', False)
        super(AtomicInstance, self).__setattr__('_attrs', {})
        super(AtomicInstance, self).__setattr__('_packer', packer)
        super(AtomicInstance, self).__setattr__('_data', consumer)
        super(AtomicInstance, self).__setattr__('_parent', parent)
        super(AtomicInstance, self).__setattr__('_namespace', namespace or [])

    def keys(self):
        return self._attrs.keys()

    @property
    def data(self):
        return self._data

    def freeze(self):
        super(AtomicInstance, self).__setattr__('_frozen', True)

    @property
    def writing(self):
        return isinstance(self.data, DataBuilder)

    def local_attr(self, name, *args):
        """Get/set a local attribute

        Parameters
        ----------
        name : str
            name of parameter
        value : optional
            if set, value to change attribute to

        Returns
        -------
        value
            if attribute is being gotten
        None
            if attribute is being set or gotten attribute has no value
        """
        if len(args):
            return super(AtomicInstance, self).__setattr__('_local_'+name,
                                                           args[0])
        else:
            try:
                return super(AtomicInstance,
                             self).__getattribute__('_local_'+name)
            except AttributeError:
                return None

    def __getattr__(self, name):
        return self._attrs[name]

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setattr__(self, name, value):
        if hasattr(self, name) and name not in self._attrs:
            return super(AtomicInstance, self).__setattr__(name, value)
        if self._frozen and name not in self._attrs:
            raise KeyError(name)
        self._attrs[name] = value

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __str__(self):
        consumer = None
        if not isinstance(self.data, DataBuilder):
            consumer = self.data
            super(AtomicInstance, self).__setattr__('_data', DataBuilder())
        try:
            value = str(self._packer.pack(self, self.data))
        except Exception as err:
            code.print_helpful_traceback()
            raise Exception('Could not pack atomic instance: %s' % err)
        if consumer is not None:
            super(AtomicInstance, self).__setattr__('_data', consumer)
        return value

    def __repr__(self):
        return '%s at 0x%x (keys=%s)' % (self.__class__.__name__, id(self),
                                         repr(self.keys()))

    def __dir__(self):
        return self.keys()


class ThinAtomicInstance(AtomicInstance):
    def __init__(self, value):
        super(AtomicInstance, self).__setattr__('_value', value)
        super(AtomicInstance, self).__setattr__('_attrs', {})
        super(AtomicInstance, self).__setattr__('_data', None)
        super(AtomicInstance, self).__setattr__('_frozen', True)

    def __str__(self):
        if self._data is not None:
            self._data += self._value
        return self._value


class DictAtomicInstance(AtomicInstance):
    def __init__(self, atom, attrs):
        super(AtomicInstance, self).__setattr__('_attrs', attrs)
        super(AtomicInstance, self).__setattr__('_packer', atom)
        super(AtomicInstance, self).__setattr__('_data', None)
        super(AtomicInstance, self).__setattr__('_frozen', True)
        super(AtomicInstance, self).__setattr__('_parent', None)
