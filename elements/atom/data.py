
__all__ = ['DataConsumer']

SEEK_RELATIVE = -1
SEEK_ROOT = -2
SEEK_TOP = 0


class DataConsumer(object):
    """
    Attributes
    ----------
    data : buffer
        Read-only data buffer
    offset : int
        Current offset of buffer
    """

    def __init__(self, parent_or_buffer):
        try:
            self._data = parent_or_buffer.data
            self.parent = parent_or_buffer
            self.offset = self.base_offset = self.parent.offset
        except:
            self._data = parent_or_buffer[:]
            self.parent = None
            self.offset = self.base_offset = 0
        self.seek_map = {}

    @property
    def data(self):
        """Read-only data"""
        return self._data

    @data.setter
    def data(self, value):
        raise TypeError('data is immutable')

    def consume(self, amount):
        self.offset += amount

    @property
    def exhausted(self):
        return self.offset-self.base_offset

    def __len__(self):
        return len(self.data)-self.offset

    def __getitem__(self, key):
        """Get a slice"""
        try:
            if not key.start:
                start = self.offset
            else:
                start = self.offset + key.start
            end = self.offset + key.stop
        except:
            raise TypeError('DataConsumer only accepts slice objects')
        data = self.data[start:end]
        self.offset = end
        return data

    def seek(self, offset, whence=SEEK_RELATIVE):
        if whence == SEEK_RELATIVE:
            self.offset += offset
        elif whence == SEEK_ROOT:
            self.offset = 0 + offset
        else:
            target = self
            for i in xrange(whence):
                target = target.parent
            self.offset = target.base_offset + offset


class DataBuilder(object):
    """
    Attributes
    ----------
    data : buffer
    offset : int
        Current offset of buffer
    """
    def __init__(self):
        self.data = ''
        self.seek_map = {}

    @property
    def offset(self):
        return len(self)

    def __len__(self):
        return len(self.data)

    def __iadd__(self, data):
        data = str(data)
        self.data += data
        return self

    def __str__(self):
        return self.data

    def __setitem__(self, key, value):
        value = str(value)
        try:
            if not key.start:
                start = 0
            else:
                start = key.start
            end = start + key.stop
        except:
            start = key
            end = start + len(value)
        self.data = self.data[:start]+value+self.data[end:]
