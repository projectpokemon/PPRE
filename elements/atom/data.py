
class DataConsumer(object):
    """
    Attributes
    ----------
    data : buffer
        Read-only data buffer
    offset : int
        Current offset of buffer
    """
    SEEK_RELATIVE = -1
    SEEK_ROOT = -2
    SEEK_TOP = 0

    def __init__(self, parent_or_buffer):
        try:
            self._data = parent_or_buffer.data
            self.parent = parent_or_buffer
            self.offset = self.base_offset = self.parent.offset
        except:
            self._data = parent_or_buffer[:]
            self.parent = None
            self.offset = self.base_offset = 0

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
        if whence == self.SEEK_RELATIVE:
            self.offset += offset
        elif whence == self.SEEK_ROOT:
            self.offset = 0 + offset
        else:
            target = self
            for i in xrange(whence):
                target = target.parent
            self.offset = target.base_offset + offset
