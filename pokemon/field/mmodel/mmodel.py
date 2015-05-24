"""
About HGSS height bans:
Bans are by natid.
OverworldSprite.attr controls how sprites are drawn.

Sprite shown is the first entry who has a matching sprite_id.
Table is searched until this sprite is found
"""
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
        # attr = 20007 for most pokemon (32x32)
        # attr = 20006 for diglett/dugtrio (won't jump?)
        # attr = 21000 for large poke sprites (64x64) (Steelix, Lugia, etc.)
        # many other values...

    def get_btx(self):
        btx = BTX(reader=self.collection.game.get_mmodel(self.file_id))
        return btx


class OverworldSprites(Editable):
    def define(self, game):
        self.game = game
        self.array('table', OverworldSprite(self).base_struct,
                   length=game.overworld_sprite_table[2])
        self.map = {}

    def load(self):
        self.map = {}
        with self.game.open('overlays_dez', 'overlay_{0:04}.bin'.format(
                self.game.overworld_sprite_table[0])) as handle:
            reader = BinaryIO.reader(handle)
            reader.seek(self.game.overworld_sprite_table[1])
            Editable.load(self, BinaryIO.reader(reader))
        for sprite in self.table:
            self.map[sprite.sprite_id] = sprite
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
        # Uses following_sprite_table
        raise NotImplementedError()


class PartnerPokemon(Editable):
    """How HGSS Partners appear.
    If oversized, they will not fit into buildings
    """
    def define(self):
        self.uint8('u0', default=0)
        self.uint8('oversized')
        self.uint8('orientation')
        # If not overworld, orientation = 0x11 for flying or 0x10 for small things
        self.uint8('u3', default=0)
