
import abc


class Archive(object):
    __metaclass__ = abc.ABCMeta
    files = {}

    def get(self, ref):
        return self.files[ref]

    def add(self, ref, data):
        self.files[ref] = data

    def delete(self, ref):
        self.files.pop(ref)

    def __iter__(self):
        return self.files

    def __len__(self):
        return len(self.files)

    def save(self, writer=None):
        return writer
