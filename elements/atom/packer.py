
import abc


class Packer(object):
    __metaclass__ = abc.ABCMeta

    def pack(self, attrs):
        packed = ''
        for entry in self.format_iterator(None):
            if not entry.ignore:
                packed += entry.pack_one(attrs[entry.name])
            else:
                packed += entry.pack_one(None)
        return packed

    @abc.abstractmethod
    def format_iterator(self, atomic=None):
        pass
