
from generic import Editable
from generic.collection import Collection2d
from util import BinaryIO


class MapMatrix(Editable):
    def define(self):
        self.uint8('width')
        self.uint8('height')
        self.uint8('has_map_definition_ids')
        self.uint8('has_mystery_zone')
        self.uint8('namelen')
        self.name = ''  # pascal string

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        Editable.load(self, reader)
        self.name = reader.read(self.namelen)
        """land_data_block = Editable()
        land_data_block.array('entries', land_data_block.uint16,
                              length=self.width*self.height)
        land_data_block.freeze()
        self.land_data_maps = land_data_block.load(reader)
        print(len(reader.read()))"""
        with self.simulate():

            if self.has_map_definition_ids:
                self.map_definitions = Collection2d(self.uint16, self.width,
                                                    self.height)
                self.map_definitions.load(reader)
            else:
                self.map_definitions = None

            if self.has_mystery_zone:
                self.mystery_details = Collection2d(self.uint8, self.width,
                                                    self.height)
                self.mystery_details.load(reader)
            else:
                self.mystery_details = None
            self.land_data_maps = Collection2d(self.uint16,
                                               self.width, self.height)
            self.land_data_maps.load(reader)

    def save(self, writer=None):
        self.namelen = len(self.name)
        writer = Editable.save(self, writer)
        writer.write(self.name)
        if self.has_map_definition_ids:
            writer = self.map_definitions.save(writer)
        if self.has_mystery_zone:
            writer = self.mystery_details.save(writer)
        writer = self.land_data_maps.save(writer)
        return writer
World = MapMatrix
