
from generic import Editable
from util import BinaryIO


class Type(object):
    def __init__(self, game):
        self.game = game
        self.name = ''
        self.names = game.text(game.locale_text_id('type_names'))

    def load_id(self, type_id):
        self.name = self.names[type_id]
        return self

    def commit(self, type_id):
        if self.name != self.names[type_id]:
            self.names[type_id] = self.name
            self.game.set_text(self.game.locale_text_id('type_names'),
                               self.names)


class TypeEffectiveness(Editable):
    def define(self, game):
        self.game = game
        if game.gen == 4:
            self.uint8('source_type')
            self.uint8('target_type')
            self.uint8('multiplier_')
            self.factor = 10.0
        else:
            self.factor = 4.0
            self.uint8('multiplier_')

    @property
    def multiplier(self):
        return self.multiplier_/self.factor

    @multiplier.setter
    def multiplier(self, value):
        self.multiplier_ = int(value*self.factor)


class EffectivenessTable(object):
    def __init__(self, game):
        self.game = game
        self.effectives = []
        self.length = 0

    def load(self):
        with self.game.open('overlays_dez', 'overlay_{0:04}.bin'.format(
                self.game.type_effectiveness_table[0])) as handle:
            reader = BinaryIO.reader(handle)
            reader.seek(self.game.type_effectiveness_table[1])
            while True:
                effect = TypeEffectiveness(self.game)
                effect.load(reader=reader)
                if effect.source_type == 0xFE and effect.target_type == 0xFE:
                    break
                self.effectives.append(effect)
        self.length = len(self.effectives)
