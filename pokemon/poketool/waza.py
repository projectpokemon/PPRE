
from generic.editable import Editable
import pokemon.game as game
from util import BinaryIO


class StatChange(Editable):
    STATS = ['hp', 'attack', 'defense', 'spatk', 'spdef', 'speed', 'accuracy',
             'evasion', 'all']

    def __init__(self, statid, level, chance):
        self.statid = statid
        self.restrictUInt8('stat')
        self.level = level
        self.restrictInt8('level')
        self.chance = chance
        self.restrictUInt8('chance')

    @property
    def stat(self):
        return self.STATS[self.statid]

    @stat.setter
    def stat(self, value):
        self.statid = self.STATS.index(value)


class Waza(Editable):
    def __init__(self, reader=None, version='Diamond'):
        self.version = version
        self.effect = 0
        self.restrictUInt16('effect')
        self.effectcategory = 0
        self.restrictUInt8('effectcategory')
        self.category = 0
        self.restrictUInt8('category')
        self.power = 0
        self.restrictUInt8('power')
        self.type = 0
        self.restrictUInt8('type')
        self.accuracy = 100
        self.restrictUInt8('accuracy')
        self.pp = 25
        self.restrictUInt8('pp')
        self.effectchance = 0
        self.restrictUInt8('effectchance')
        self.flag1 = 0
        self.restrictUInt16('flag1')
        self.priority = 0
        self.restrictInt8('priority')
        self.flag2 = 0
        self.restrictUInt8('flag2')
        self.minhits = 0
        self.restrict('minhits', min_value=0, max_value=0xF)
        self.maxhits = 0
        self.restrict('maxhits', min_value=0, max_value=0xF)
        self.status = 0
        self.restrictUInt8('status')
        self.minturns = 0
        self.restrictUInt8('minturns')
        self.maxturns = 0
        self.restrictUInt8('maxturns')
        self.crit = 0
        self.restrictUInt8('crit')
        self.flinch = 0
        self.restrictUInt8('flinch')
        self.recoil = 0
        self.restrictInt8('recoil')
        self.healing = 0
        self.restrictInt8('healing')
        self.target = 0
        self.restrictUInt8('target')
        self.stats = []
        self.restrict('stats', max_length=3)

        if reader is not None:
            self.load(reader)

    def load(self, reaader):
        reader = BinaryIO.reader(reader)

    def save(self, writer=None):
        writer = BinaryIO() if writer is None else writer
        return writer
