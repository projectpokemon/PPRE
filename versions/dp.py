
from rawdb.versions.base import GameVersion
from rawdb.elements.atom import BaseAtom


class BaseStatAtomDiamond(BaseAtom):
    def __init__(self):
        super(BaseStatAtomDiamond, self).__init__()
        self.uint8('basehp')
        self.uint8('baseatk')
        self.uint8('basedef')
        self.uint8('basespeed')
        self.uint8('basespatk')
        self.uint8('basespdef')
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


class Diamond(GameVersion):
    base_stat_file = 'poketool/personal/personal.narc'
    base_stat_atom = BaseStatAtomDiamond


class Pearl(Diamond):
    pass
