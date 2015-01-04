
from pokemon import game
from generic.editable import XEditable as Editable


class WalkEncouter(Editable):
    def define(self, version, level=True):
        if level:
            self.uint32('level')
        if version < game.Version(4, 3):
            self.uint32('natid')
        else:
            self.uint16('natid')


class WaterEncouter(Editable):
    def define(self, version):
        if version < game.Version(4, 3):
            self.uint8('maxlevel')
            self.uint8('minlevel')
            self.uint16('padding')
            self.uint32('natid')
        else:
            self.uint8('maxlevel')
            self.uint8('minlevel')
            self.uint16('natid')


class Walking(Editable):
    def define(self, version):
        natid_only_s = WalkEncouter(version, False).base_struct
        if version < game.Version(4, 3):
            self.uint32('rate')
            self.array('normal', WalkEncouter(version).base_struct, length=12)
            for time in ('morning', 'day', 'night'):
                self.array(time, natid_only_s, length=2)
            self.array('radar', natid_only_s, length=4)
            self.array('unknown', self.uint32, length=2)  # two identical. 0 or 100
            self.array('padding', self.uint32, length=3)
            self.uint32('unown')
            for name in ('ruby', 'sapphire', 'emerald', 'firered', 'leafgreen'):
                self.array(name, natid_only_s, length=2)
        else:
            num_pokemon = 12
            self.array('levels', self.uint8, length=num_pokemon)
            self.array('morning', natid_only_s, length=num_pokemon)
            self.array('day', natid_only_s, length=num_pokemon)
            self.array('night', natid_only_s, length=num_pokemon)
            self.array('hoenn', natid_only_s, length=2)
            self.array('sinnoh', natid_only_s, length=2)


class Water(Editable):
    def define(self, name, version):
        self.name = 'Water_'+name
        if version < game.Version(4, 3):
            self.uint32('rate')
        num_pokemon = 5
        if version >= game.Version(4, 3) and name == 'rocksmash':
            num_pokemon = 2
        self.array('normal', WaterEncouter(version).base_struct,
                   length=num_pokemon)


class Encounters(Editable):
    def define(self, version=game.Version(4, 0)):
        if version >= game.Version(4, 3):
            self.uint8('walkrate')
            self.uint8('surfrate')
            self.uint8('rocksmashrate')
            self.uint8('oldrodrate')
            self.uint8('goodroodrate')
            self.uint8('superrodrate')
            self.uint16('padding')
        self.struct('walking', Walking(version).base_struct)
        for water in ('surf', 'rocksmash', 'oldrod', 'goodrod', 'superrod'):
            self.struct(water, Water(water, version).base_struct)
        if version >= game.Version(4, 3):
            self.array('radio', WalkEncouter(version, False).base_struct,
                       length=2)
