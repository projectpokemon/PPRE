
import abc


class Packer(object):
    __metaclass__ = abc.ABCMeta

    def pack(self, atomic, data):
        for entry in self.format_iterator(None):
            data += entry.pack_one(atomic)
        return data

    def format_iterator(self, atomic=None):
        return []
