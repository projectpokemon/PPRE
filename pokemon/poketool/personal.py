
from generic.editable import Editable
import pokemon.game as game
from util import BinaryIO, lget


class Stats(Editable):
    STATS = ['hp', 'attack', 'defense', 'speed', 'spatk', 'spdef']

    def __init__(self, hp, attack, defense, speed, spatk, spdef,
                 **restrict_kwargs):
        self.setall(hp, attack, defense, speed, spatk, spdef)
        self.restrictUInt8('hp', **restrict_kwargs)
        self.restrictUInt8('attack', **restrict_kwargs)
        self.restrictUInt8('defense', **restrict_kwargs)
        self.restrictUInt8('speed', **restrict_kwargs)
        self.restrictUInt8('spatk', **restrict_kwargs)
        self.restrictUInt8('spdef', **restrict_kwargs)

    def setall(self, hp, attack, defense, speed, spatk, spdef):
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.spatk = spatk
        self.spdef = spdef

    def __iter__(self):
        for i in xrange(6):
            yield (self.STATS[i], self[i])

    def __getitem__(self, key):
        try:
            key = self.STATS[key]
        except KeyError:
            pass
        return getattr(self, key)


class Personal(Editable):

    def __init__(self, reader=None, version='Diamond'):
        self.version = version
        self.base_stat = Stats(0, 0, 0, 0, 0, 0)
        self.restrict('base_stat')
        self.types = [0]
        self.restrict('types', max_length=2)
        self.catchrate = 255

        def validate_mod(editable, name, value, mod):
            if not value % mod:
                raise ValueError('{0} Not mod {1}'.format(value, mod))
        self.restrictUInt8('catchrate')
        self.baseexp = 0
        if self.version in game.GEN_IV:
            self.restrictUInt8('baseexp')
        else:
            self.restrictUInt16('baseexp')
        self.evs = Stats(0, 0, 0, 0, 0, 0, max_value=3)
        self.restrict('evs')
        self.items = []
        self.restrict('items',
                      max_length=2 if self.version in game.GEN_VI else 3)
        self.gender = 0  # TODO: Better type like enum? or m/f/n rates?
        self.restrictUInt8('gender')
        self.hatchsteps = 256
        self.restrictUInt16('hatchsteps')
        self.happiness = 70
        self.restrictUInt8('happiness')
        self.growth = 0  # Exp growth rate
        self.restrictUInt8('growth')
        self.egggroups = [15]
        self.restrict('egggroups', max_length=2)
        self.abilities = []
        self.restrict('abilities',
                      max_length=2 if self.version in game.GEN_VI else 3)
        self.flee = 0
        self.restrictUInt8('flee')
        self.color = 0
        self.restrictUInt8('color')
        self.tms = []  # List of known TMs
        self.restrict('tms', max_length=13*8)
        if self.version in game.GEN_V:
            # TODO: Restrictions here
            self.stage = 1
            self.height = 0
            self.weight = 0
            self.formid = 0
            self.form = 0
            self.numforms = 1
        elif self.version in game.GEN_VI:
            raise NotImplementedError('Gen VI not supported yet')
        else:
            self.stage = None
            self.height = None
            self.weight = None
            self.formid = None
            self.form = None
            self.numforms = None
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.base_stat.setall(*[reader.readUInt8() for i in xrange(6)])
        self.types = [reader.readUInt8(), reader.readUInt8()]
        self.catchrate = reader.readUInt8()
        if self.version in game.GEN_V:
            self.stage = reader.readUInt8()
        else:
            self.baseexp = reader.readUInt8()
        evs = reader.readUInt16()
        self.evs.setall(*[(evs >> i) & 3 for i in xrange(0, 12, 2)])
        self.items = [reader.readUInt16(), reader.readUInt16()]
        if self.version in game.GEN_V:
            self.items.append(reader.readUInt16())
        self.gender = reader.readUInt8()
        self.hatchsteps = reader.readUInt8() << 8
        self.happiness = reader.readUInt8()
        self.growth = reader.readUInt8()
        self.egggroups = [reader.readUInt8(), reader.readUInt8()]
        self.abilities = [reader.readUInt8(), reader.readUInt8()]
        if self.version in game.GEN_V:
            self.abilities.append(reader.readUInt8())
            self.flee = reader.readUInt8()
            self.formid = reader.readUInt16()
            self.form = reader.readUInt16()
            self.numforms = reader.readUInt8()
            self.color = reader.readUInt8()
            self.baseexp = reader.readUInt16()
            self.height = reader.readUInt16()
            self.weight = reader.readUInt16()
        else:
            self.flee = reader.readUInt8()
            self.color = reader.readUInt8()
        reader.read(2)
        self.tms = []
        for i in xrange(13):
            tmx = reader.readUInt8()
            for j in xrange(8):
                if (tmx >> j) & 0x1:
                    self.tms.append(i*8+j+1)

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        for stat, value in self.base_stat:
            writer.writeUInt8(value)
        if not len(self.types):
            raise ValueError('Pokemon must have at least one type')
        for i in xrange(2):
            writer.writeUInt8(lget(self.types, i, self.types[0]))
        writer.writeUInt8(self.catchrate)
        writer.writeUInt8(self.baseexp)
        evs = 0
        for i in xrange(0, 12, 2):
            evs |= (self.evs[i/2] & 0x3) << i
        writer.writeUInt16(evs)
        for i in xrange(3 if self.version in game.GEN_V else 2):
            writer.writeUInt16(lget(self.items, i, 0))
        writer.writeUInt8(self.gender)
        writer.writeUInt8(self.hatchsteps >> 8)
        writer.writeUInt8(self.happiness)
        writer.writeUInt8(self.growth)
        if not len(self.egggroups):
            raise ValueError('Pokemon must have at least one egg group')
        for i in xrange(2):
            writer.writeUInt8(lget(self.egggroups, i, self.egggroups[0]))
        for i in xrange(3 if self.version in game.GEN_V else 2):
            writer.writeUInt8(lget(self.abilities, i, 0))
        if self.version in game.GEN_V:
            writer.writeUInt8(self.flee)
            writer.writeUInt16(self.formid)
            writer.writeUInt16(self.form)
            writer.writeUInt8(self.numforms)
            writer.writeUInt8(self.color)
            writer.writeUInt16(self.baseexp)
            writer.writeUInt16(self.height)
            writer.writeUInt16(self.weight)
        else:
            writer.writeUInt8(self.flee)
            writer.writeUInt8(self.color)
        writer.writeUInt16(0)  # padding
        for i in xrange(13):
            tmx = 0
            for j in xrange(8):
                if i*8+j+1 in self.tms:
                    tmx |= 1 << j
            writer.writeUInt8(tmx)
        writer.writeAlign(4)
        return writer
