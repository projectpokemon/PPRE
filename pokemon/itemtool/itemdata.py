
from pokemon import game
from pokemon.poketool.personal import Stats as EVStats
from generic.editable import XEditable as Editable


class Stats(Editable):
    STATS = ['hp', 'attack', 'defense', 'spatk', 'spdef', 'speed',
             'acc', 'crit']

    def define(self, num=8, width=4):
        for stat in self.STATS[:num]:
            if width is not None:
                self.int8(stat, width=width, max_value=7, min_value=-8)
            else:
                self.int8(stat)


class Boosts(Editable):
    def define(self):
        self.uint8('hp', width=2)
        self.uint8('level', width=1)
        self.uint8('evolution', width=1)
        self.int8('attack', width=4)
        self.int8('defense', width=4)
        self.int8('spatk', width=4)
        self.int8('spdef', width=4)
        self.int8('speed', width=4)
        self.int8('acc', width=4)
        self.int8('crit', width=2)
        self.uint8('pp', width=2)


class ItemData(Editable):
    def define(self, version=game.Version(4, 0)):
        self.version = version
        self.uint16('price')
        self.uint8('battleeffect')
        self.uint8('gain')
        self.uint8('berry')
        self.uint8('flingeffect')
        self.uint8('flingpower')
        self.uint8('naturalgiftpower')
        self.uint8('flag')
        self.uint8('pocket')
        self.uint8('type')
        self.uint8('category')
        self.uint16('u0')  # 1 for everything except pokeballs, orbs, mail, hold items
        self.uint8('index')
        self.struct('statboosts', Boosts().base_struct)
        self.uint16('target')
        self.struct('evs', EVStats().base_struct)
        self.uint8('hprestore')
        self.int8('pprestore')
        self.array('happy', self.int8, length=3)
