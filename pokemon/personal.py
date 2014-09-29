
from collections import namedtuple

from rawdb.util.io import BinaryIO


Stats = namedtuple('Stats', 'hp attack defense speed spatk spdef')


class Personal(object):
    def __init__(self, reader=None):
        self.base_stat = Stats(0, 0, 0, 0, 0, 0)
        self.types = []
        self.catchrate = 255
        self.baseexp = 0
        self.evs = Stats(0, 0, 0, 0, 0, 0)
        self.items = []
        self.gender = 0  # TODO: Better type like enum? or m/f/n rates?
        self.hatchsteps = 256
        self.happiness = 70
        self.growth = 0  # Exp growth rate
        self.egggroups = []
        self.abilities = []
        self.flee = 0
        self.color = 0
        self.tms = []  # List of known TMs
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        self.base_stat = Stats._make([reader.readUInt8() for i in xrange(6)])
        self.types = [reader.readUInt8(), reader.readUInt8()]
        self.catchrate = reader.readUInt8()
        self.baseexp = reader.readUInt8()
        evs = reader.readUInt16()
        self.evs = Stats._make([(evs >> i) & 3 for i in xrange(0, 12, 2)])
        self.items = [reader.readUInt16(), reader.readUInt16()]
        self.gender = reader.readUInt8()
        self.hatchsteps = reader.readUInt8() << 8
        self.happiness = reader.readUInt8()
        self.growth = reader.readUInt8()
        self.egggroups = [reader.readUInt8(), reader.readUInt8()]
        self.abilities = [reader.readUInt8(), reader.readUInt8()]
        self.flee = reader.readUInt8()
        self.color = reader.readUInt8()
        reader.read(2)
        self.tms = []
        for i in xrange(13):
            tmx = reader.readUInt8()
            for j in xrange(8):
                if (tmx >> j) & 0x1:
                    self.tms.append(i*8+j+1)
