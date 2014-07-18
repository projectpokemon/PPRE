
import struct

from rawdb.versions.base import GameVersion
from rawdb.elements.atom import BaseAtom, AtomicInstance


STATS = ['hp', 'atk', 'def', 'speed', 'spatk', 'spdef']


class BaseStatAtomic(AtomicInstance):
    def __getattr__(self, name):
        try:
            if name[:2] == 'ev':
                # hp are LSBs (evs >> 0 & 0x3)
                shift = STATS.index(name[2:])*2
                return (self.evs >> shift) & 0x3
            elif name[:2] == 'tm':
                tmid = int(name[2:])-1
                byte = tmid >> 3
                shift = tmid % 8
                return (self['tms%d' % byte] >> shift) & 0x1
            raise
        except:
            return super(BaseStatAtomic, self).__getattr__(name)

    def __setattr__(self, name, value):
        try:
            if name[:2] == 'ev':
                shift = STATS.index(name[2:])*2
                evs = self.evs
                evs &= ~(0x3 << shift)
                self.evs = evs | (value & 0x3) << shift
            elif name[:2] == 'tm':
                tmid = int(name[2:])-1
                byte = tmid >> 3
                shift = tmid % 8
                if value:
                    self['tms%d' % byte] |= 0x1 << shift
                else:
                    self['tms%d' % byte] &= ~(0x1 << shift)
            raise
        except:
            return super(BaseStatAtomic, self).__setattr__(name, value)

    def keys(self):
        old = super(BaseStatAtomic, self).keys()
        new_keys = [key for key in old if key[:2] not in ('ev', 'tm')]
        for stat in STATS:
            new_keys.append('ev'+stat)
        for tmid in xrange(13*8):
            new_keys.append('tm%d' % tmid)
        return new_keys


class BaseStatAtomDiamond(BaseAtom):
    atomic = BaseStatAtomic

    def __init__(self):
        super(BaseStatAtomDiamond, self).__init__()
        for stat in STATS:
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
            self.uint8('tms%d' % i)
        self.padding(3)


class EvolutionAtomDiamond(BaseAtom):
    def __init__(self):
        super(EvolutionAtomDiamond, self).__init__()
        for i in xrange(7):
            self.uint16('method%d' % i)
            self.uint16('param%d' % i)
            self.uint16('target%d' % i)
        self.padding(2)


class LevelMoveAtomic(AtomicInstance):
    def __getattr__(self, name):
        try:
            if name[:5] == 'level':
                lvlid = int(name[5:])
                return (self['lvlmoves'][lvlid] >> 9) & 0x7F
            elif name[:4] == 'move':
                lvlid = int(name[4:])
                return self['lvlmoves'][lvlid] & 0x1FF
            raise
        except:
            return super(LevelMoveAtomic, self).__getattr__(name)

    def __setattr__(self, name, value):
        try:
            if name[:5] == 'level':
                lvlid = int(name[5:])
                lvlmove = self['lvlmoves'][lvlid]
                value &= 0x7F
                self['lvlmoves'][lvlid] = (lvlmove & 0x1FF) | (value << 9)
            elif name[:4] == 'move':
                lvlid = int(name[4:])
                lvlmove = self['lvlmoves'][lvlid]
                value &= 0x1FF
                self['lvlmoves'][lvlid] = value | (lvlmove & (0x7F << 9))
            raise
        except:
            return super(LevelMoveAtomic, self).__setattr__(name, value)

    def keys(self):
        new_keys = []
        for lvlid in xrange(20):
            new_keys.append('level%d' % lvlid)
            new_keys.append('move%d' % lvlid)
        return new_keys


class LevelMoveAtomDiamond(BaseAtom):
    atomic = LevelMoveAtomic

    def __init__(self):
        super(LevelMoveAtomDiamond, self).__init__()
        self.array(self.uint16('lvlmoves'), terminator=0xffff)


class Diamond(GameVersion):
    base_stat_file = 'poketool/personal/personal.narc'
    base_stat_atom = BaseStatAtomDiamond
    evolution_file = 'poketool/personal/evo.narc'
    evolution_atom = EvolutionAtomDiamond
    level_moves_file = 'poketool/personal/wotbl.narc'
    level_moves_atom = LevelMoveAtomDiamond


class Pearl(Diamond):
    pass


class Platinum(Diamond):
    pass
