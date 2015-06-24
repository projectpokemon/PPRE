
from generic import Editable


class TrainerPokemon(Editable):
    def define(self, trainer):
        self.trainer = trainer
        self.uint8('ai')
        self.uint8('flag')
        self.uint16('level')
        self.uint16('natid', width=10)
        self.uint16('forme', width=6)
        self.moves = []
        self.attribute('moves')
        self.item = 0
        self.attribute('item')

    def load(self, reader):
        Editable.load(self, reader)
        if self.trainer.hold_items:
            self.item = reader.readUInt16()
        if self.trainer.movesets:
            self.moves = [reader.readUInt16() for i in range(4)]
        return self

    def save(self, writer):
        writer = Editable.save(writer)
        if self.trainer.hold_items:
            writer.writeUInt16(self.item)
        if self.trainer.movesets:
            for move in self.moves:
                writer.writeUInt16(move)
        return writer


class Trainer(Editable):
    def define(self, game):
        self.game = game
        self.uint8('movesets', width=1)
        self.uint8('hold_items', width=1)
        self.uint8('pad0', width=6)
        self.uint8('class')
        self.uint8('battle_type')
        self.uint8('num_pokemon')
        self.array('items', self.uint16, length=4)
        self.uint32('ai')
        self.uint8('battle_type2')
        self.pokemon = None

    def load_pokemon(self, reader):
        self.pokemon = []
        for i in range(self.num_pokemon):
            self.pokemon.append(TrainerPokemon(self, reader=reader))

    def save(self, writer):
        self.update()
        return Editable.save(writer)

    def save_pokemon(self, writer):
        self.update()
        for poke in self.pokemon:
            writer = poke.save(writer)
        return writer

    def update(self):
        if self.pokemon is not None:
            self.num_pokemon = len(self.pokemon)
            for poke in self.pokemon:
                if any(poke.moves):
                    self.movesets = 1
                    break
            else:
                self.movesets = 0
            for poke in self.pokemon:
                if poke.item:
                    self.hold_items = 1
                    break
            else:
                self.hold_items = 0
