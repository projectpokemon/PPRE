
import array
import itertools

from PIL import Image

from generic.editable import XEditable as Editable


class Cell(Editable):
    def define(self, attrs):
        self.uint16('num')
        self.uint16('attr')
        self.uint16('data_offset')
        if attrs & 0x1:
            self.int16('maxX')
            self.int16('maxY')
            self.int16('minX')
            self.int16('minY')


class CEBK(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='KBEC')
        self.uint32('size_')
        self.uint16('num')
        self.uint16('attrs')
        self.uint32('headersize', default=0x18)
        self.uint32('format')
        self.uint32('u0')
        self.uint32('u1')
        self.uint32('u2')
        self.cells = []

    def load(self, reader):
        Editable.load(self, reader)
        self.cells = [Cell(self.attrs, reader=reader)]


class LABL(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='LBAL')
        self.uint32('size_')
        self.names = []

    def load(self, reader):
        Editable.load(self, reader)
        offsets = []
        while True:
            offset = reader.readUInt32()
            if offset > self.size_:
                break
            offsets.append(offset)
        start = reader.tell()-4
        for offset in self.offsets:
            with reader.seek(start+offset):
                self.names.append(reader.readString())


class NCER(Editable):
    def define(self):
        self.string('magic', length=4, default='RECN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.cebk = CEBK(self)
        self.labl = LABL(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.cebk.load(reader)

    def save(self, writer=None):
        writer = Editable.save(self, writer)
        writer = self.cebk.save(writer)
        return writer
