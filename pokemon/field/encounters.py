
from pokemon import game
from generic.editable import XEditable as Editable


class WalkEncouter(Editable):
    def define(self, level=True):
        if level:
            self.uint32('level')
        self.uint32('natid')


class WaterEncouter(Editable):
    def define(self):
        self.uint8('minlevel')
        self.uint8('maxlevel')
        self.uint16('padding')
        self.uint32('natid')


class Walking(Editable):
    def define(self):
        self.uint32('rate')
        self.array('normal', WalkEncouter().base_struct, length=12)
        natid_only_s = WalkEncouter(False).base_struct
        for time in ('morning', 'day', 'night'):
            self.array(time, natid_only_s, length=2)
        self.array('radar', natid_only_s, length=4)
        self.array('unknown', self.uint32, length=2)  # two identical. 0 or 100
        self.array('padding', self.uint32, length=3)
        self.uint32('unown')
        for game in ('ruby', 'sapphire', 'emerald', 'firered', 'leafgreen'):
            self.array(game, natid_only_s, length=2)


class Water(Editable):
    def define(self):
        self.uint32('rate')
        self.array('normal', WaterEncouter().base_struct, length=5)


class Encounters(Editable):
    def define(self, version='Diamond'):
        self.struct('walking', Walking().base_struct)
        for water in ('surf', 'unknownwater', 'oldrod', 'goodrod', 'superrod'):
            self.struct(water, Water().base_struct)
