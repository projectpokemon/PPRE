
from generic import Editable
from util import BinaryIO
from ntr.g3d.btx import BTX


class OverworldSprite(Editable):
    def define(self, collection):
        self.collection = collection
        self.uint16('sprite_id')
        self.uint16('file_id')
        self.uint16('attr')
        # attr = 0 for most normal people
        # attr = 20007 for most pokemon
        # attr = 20006 for diglett/dugtrio (won't jump?)
        # attr = 21000 for large poke sprites (Steelix, Lugia, etc.)
        # many other values...

    def get_btx(self):
        btx = BTX(reader=self.collection.game.get_mmodel(self.file_id))
        return btx


class OverworldSprites(Editable):
    def define(self, game):
        self.game = game
        self.array('table', OverworldSprite(self).base_struct, length=1100)
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

    def save(self):
        with self.game.open('overlays_dez', 'overlay_{0:04}.bin'.format(
                self.game.overworld_sprite_table[0]), mode='r+') as handle:
            writer = BinaryIO.writer(handle)
            writer.seek(self.game.overworld_sprite_table[1])
            Editable.save(self, writer)

    def __getitem__(self, key):
        return self.map[key]

    def get_pokemon_sprite(self, natid, forme=0):
        if forme:
            raise NotImplementedError('Forme handling not enabled yet')
        return self.table[natid+215]
