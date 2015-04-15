
from generic import Editable
from util import BinaryIO


class MapMatrix(Editable):
    def define(self):
        self.uint8('width')
        self.uint8('height')
        self.uint8('u2')
        self.uint8('u3')
        self.uint8('namelen')
        self.name = ''  # pascal string
        self.scripts = []

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        Editable.load(self, reader)
        self.name = reader.read(self.namelen)
        script_block = Editable()
        script_block.array('entries', script_block.uint16,
                           length=self.width*self.height)
        script_block.freeze()
        self.scripts = script_block.load(reader)

    def __getitem__(self, key):
        try:
            idx = key[1]*self.width+key[0]
        except (IndexError, TypeError):
            raise KeyError('MapMatrix expects a two-tuple index')
        return self.scripts.entries[idx]
World = MapMatrix
