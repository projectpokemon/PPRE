
from generic import Editable
import pokemon.game as game
from util import BinaryIO


class StatChange(Editable):
    STATS = ['hp', 'attack', 'defense', 'spatk', 'spdef', 'speed', 'accuracy',
             'evasion', 'all']

    def define(self):
        self.uint8('stat_id')
        self.uint8('level')
        self.uint8('chance')

    @property
    def stat(self):
        return self.STATS[self.stat_id]

    @stat.setter
    def stat(self, value):
        self.stat_id = self.STATS.index(value)


class Waza(Editable):
    TARGET_SINGLE = 0
    TARGET_ANY = 1
    TARGET_RANDOM = 2
    TARGET_BOTH = 4
    TARGET_ALL = 8
    TARGET_SELF = 16
    TARGET_TEAM = 32
    TARGET_FIELD = 64
    TARGET_OPPOSITE_FIELD = 128
    TARGET_PARTNER = 256
    TARGET_ALLIES = 512
    TARGET_ACTING_FOE = 1024

    def define(self, game):
        self.game = game
        if game.gen == 4:
            self.uint16('effect')
            self.uint8('category')
            self.uint8('power', default=70)
            self.uint8('type')
            self.uint8('accuracy', default=100)
            self.uint8('pp', default=15)
            self.uint8('effect_chance')
            self.uint16('target')
            self.int8('priority')
            self.uint8('contact', width=1)
            self.uint8('protected', width=1)
            self.uint8('magic_bounced', width=1)
            self.uint8('snatchable', width=1)
            self.uint8('u8_5', width=1)
            self.uint8('u8_6', width=1)
            self.uint8('u8_7', width=1)
            self.uint8('u8_8', width=1)
            self.uint8('contest_effect')
            self.uint8('contest_type')
            self.uint16('pad_e')
        else:
            self.uint16('effect')
            self.uint8('effect_category')
            self.uint8('category')
            self.uint8('power')
            self.uint8('type')
            self.uint8('accuracy', default=100)
            self.uint8('pp', default=15)
            self.uint8('effect_chance')
            self.uint16('flag1')
            self.int8('priority')
            self.uint8('flag2')
            self.uint8('minhits', width=4)
            self.uint8('maxhits', width=4)
            self.uint8('status')
            self.uint8('minturns')
            self.uint8('maxturns')
            self.uint8('crit')
            self.uint8('flinch')
            self.int8('recoil')
            self.int8('healing')
            self.uint8('target')
            self.stats = []
            self.restrict('stats', max_length=3)
