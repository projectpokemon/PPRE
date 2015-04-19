
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
        self.land_data_maps = []

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        Editable.load(self, reader)
        self.name = reader.read(self.namelen)
        land_data_block = Editable()
        land_data_block.array('entries', land_data_block.uint16,
                              length=self.width*self.height)
        land_data_block.freeze()
        self.land_data_maps = land_data_block.load(reader)

    def __getitem__(self, key):
        try:
            idx = key[1]*self.width+key[0]
        except (IndexError, TypeError):
            raise KeyError('MapMatrix expects a two-tuple index')
        return self.land_data_maps.entries[idx]

    def __setitem__(self, key, value):
        try:
            idx = key[1]*self.width+key[0]
        except (IndexError, TypeError):
            raise KeyError('MapMatrix expects a two-tuple index')
        self.land_data_maps.entries[idx] = value
World = MapMatrix
