
import abc
import zipfile

from rawdb.util.io import BinaryIO


class Archive(object):
    __metaclass__ = abc.ABCMeta
    files = {}
    extension = '.bin'

    def get(self, ref):
        return self.files[ref]

    def add(self, ref, data):
        self.files[ref] = data

    def reset(self):
        """Resets archive"""
        self.__init__()

    def delete(self, ref):
        self.files.pop(ref)

    def flush(self):
        pass

    def __iter__(self):
        return self.files

    def __len__(self):
        return len(self.files)

    def save(self, writer=None):
        return writer

    def get_value(self):
        """String of this Archive"""
        writer = BinaryIO()
        return self.save(writer).getvalue()

    def export(self, handle, mode='w'):
        """Build a zip archive from files

        Parameters
        ----------
        handle : File-like or string
            Destination file handle to write to
        """
        with zipfile.ZipFile(handle, mode) as archive:
            try:
                names = self.files.keys()
            except AttributeError:
                names = xrange(len(self.files))
            for name in names:
                archive.writestr(str(name)+self.extension, self.files[name])
        return handle

    def import_(self, handle, mode='r'):
        """Import files from the zip archive into this

        Parameters
        ----------
        handle : File-like or string
            Target file handle to read from
        mode : string
            Mode to read from handle
        """
        self.reset()
        with zipfile.ZipFile(handle, mode) as archive:
            for name in archive.namelist():
                if name.endswith(self.extension):
                    internalname = name[:-len(self.extension)]
                else:
                    internalname = name
                self.add(internalname, archive.read(name))
        self.flush()


class ArchiveList(Archive):
    files = []

    def get(self, ref):
        return self.files[ref]

    def add(self, ref=None, data=''):
        self.files.append(data)
