
from rawdb.versions.base import GameVersion
from rawdb.elements.atom import BaseAtom


class BaseStatAtomDiamond(BaseAtom):
    def __init__(self):
        super(BaseStatAtomDiamond, self).__init__()
        self.stats = ['hp', 'atk', 'def', 'speed', 'spatk', 'spdef']
        for stat in self.stats:
            self.uint8('base'+stat)
        self.uint8('type1')
        self.uint8('type2')
        self.uint8('catchrate')
        self.uint8('baseexp')
        self.uint16('evs')
        self.uint16('item1')
        self.uint16('item2')
        self.uint8('gender')
        self.uint8('hatchcycle')
        self.uint8('basehappy')
        self.uint8('exprate')
        self.uint8('egggroup1')
        self.uint8('egggroup2')
        self.uint8('ability1')
        self.uint8('ability2')
        self.uint8('flee')
        self.uint8('color')
        self.padding(2)
        for i in xrange(13):
            self.uint8('tm%d' % i)
        self.padding(3)


class EvolutionAtomDiamond(BaseAtom):
    def __init__(self):
        super(EvolutionAtomDiamond, self).__init__()
        for i in xrange(7):
            self.uint16('method%d' % i)
            self.uint16('param%d' % i)
            self.uint16('target%d' % i)
        self.padding(2)


class Diamond(GameVersion):
    base_stat_file = 'poketool/personal/personal.narc'
    base_stat_atom = BaseStatAtomDiamond


class Pearl(Diamond):
    pass
