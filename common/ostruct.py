import struct
from collections import OrderedDict


class OStructContents(dict):
    """Dictionary which acts as a class with its keys as attributes

    >>> osc = OStructContents({'a': 1, 'b': 2})
    >>> osc['A']
    1
    >>> osc.B
    2

    """
    def __dir__(self):
        return self.keys()

    def __getattr__(self, name):
        return self[name]


class OStruct(OrderedDict):
    """A pair-readable struct parser

    """
    def __init__(self, iterable):
        OrderedDict.__init__(self, iterable)
        self._struct = struct.Struct(''.join(self.values()))
        self.size = self._struct.size

    def unpack(self, data_or_handle):
        """Unpacks data

        Parameters
        ----------
        data_or_handle: string or file
            target to read from

        Returns
        -------
        contents: OStructContents

        """
        if isinstance(data_or_handle, file):
            data = data_or_handle.read(self.size)
        else:
            data = data_or_handle[:self.size]
        conts = self._struct.unpack(data)
        return OStructContents(zip(self.keys(), conts))
