
from generic import Editable


class LandDataMap(Editable):
    def define(self, game):
        self.game = game
        self.uint32('permission_size')
        self.uint32('objects_size')
        self.uint32('bmd_size')
        self.uint32('bdhc_size')
        self.uint32('u10')
