
from generic import Editable
from util import BinaryIO
from ntr.g3d.btx import BTX


class OverworldSprite(Editable):
    def define(self, collection):
        self.collection = collection
        self.uint16('u0')
        self.uint16('sprite_id')
        self.uint16('file_id')

    def get_btx(self):
        btx = BTX(self.collection.game.get_mmodel(self.file_id))
        return btx


class OverworldSprites(Editable):
    def define(self, game):
        self.game = game
        self.array('table', OverworldSprite(self).base_struct, length=1000)
        self.map = {}

    def load(self):
        self.map = {}
        with self.game.open('overlays_dez', 'overlay_{0:04}.bin'.format(
                self.game.overworld_sprite_table[0])) as handle:
            reader = BinaryIO.reader(handle)
            reader.seek(self.game.overworld_sprite_table[1])
            Editable.load(self, BinaryIO.reader(reader))
        for sprite in self.table:
            self.map[sprite.sprite_id] = sprite.file_id
        return self

    def __getitem__(self, key):
        return self.map[key]
