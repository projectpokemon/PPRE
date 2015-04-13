
import array
import itertools

from PIL import Image

from generic.editable import XEditable as Editable


class CellAttributes(Editable):
    """

    http://problemkaputt.de/gbatek.htm#lcdobjoamattributes
    """
    MODE_NORMAL = 0
    MODE_TRANSLUCENT = 1
    MODE_WINDOW = 2
    SHAPE_SQUARE = 0
    SHAPE_HORIZONTAL = 1
    SHAPE_VERTICAL = 2

    def define(self):
        self.uint16('attr0')
        self.uint16('attr1')
        self.uint16('attr2')

    @property
    def y(self):
        value = self.attr0 & 0xFF
        if value > 0x80:
            value -= 0x100
        return value

    @y.setter
    def y(self, value):
        if value < 0:
            value += 0x100
        self.attr0 = (self.attr0 & ~0xFF) | value

    @property
    def x(self):
        value = self.attr1 & 0x1FF
        if value > 0x100:
            value -= 0x200
        return value

    @x.setter
    def x(self, value):
        if value < 0:
            value += 0x200
        self.attr1 = (self.attr1 & ~0x1FF) | value

    @property
    def width(self):
        return {self.SHAPE_SQUARE: [8, 16, 32, 64],
                self.SHAPE_HORIZONTAL: [16, 32, 32, 64],
                self.SHAPE_VERTICAL: [8, 8, 16, 32]
                }.get(self.shape)[self.size]

    @property
    def height(self):
        return {self.SHAPE_SQUARE: [8, 16, 32, 64],
                self.SHAPE_HORIZONTAL: [8, 8, 16, 32],
                self.SHAPE_VERTICAL: [16, 32, 32, 64]
                }.get(self.shape)[self.size]

    @property
    def tile_id(self):
        return self.attr2 & 0x3FF

    @property
    def palette(self):
        return (self.attr2 >> 12) & 0x7

    @property
    def rotscale(self):
        return (self.attr0 >> 8) & 0x1 == 0x1

    @property
    def scale(self):
        if (self.attr0 >> 8) & 0x3 == 0x3:
            return 2
        return 1

    @property
    def disabled(self):
        if (self.attr0 >> 8) & 0x3 == 0x2:
            return True
        return False

    @property
    def mode(self):
        return (self.attr0 >> 10) & 0x3

    @property
    def mosaic(self):
        return (self.attr0 >> 12) & 0x1 == 0x1

    @property
    def palformat(self):
        return (self.attr0 >> 13) & 0x1

    @property
    def shape(self):
        return (self.attr0 >> 14) & 0x3

    # TODO: rotscale params

    @property
    def horizontal_flip(self):
        return self.rotscale and (self.attr1 >> 12) & 0x1 == 0x1

    @property
    def vertical_flip(self):
        return self.rotscale and (self.attr1 >> 13) & 0x1 == 0x1

    @property
    def size(self):
        return (self.attr1 >> 14) & 0x3

    @property
    def z_index(self):
        return (self.attr2 >> 10) & 0x3


class Cell(Editable):
    def define(self, attrs):
        self.uint16('num')
        self.uint16('attr')
        self.uint32('data_offset')
        if attrs & 0x1:
            self.int16('maxX')
            self.int16('maxY')
            self.int16('minX')
            self.int16('minY')
        self.attrs = []


class CEBK(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='KBEC')
        self.uint32('size_')
        self.uint16('num')
        self.uint16('attrs')
        self.uint32('headersize', default=0x18)
        self.uint32('shift')
        self.uint32('u0')
        self.uint32('u1')
        self.uint32('u2')
        self.cells = []

    def load(self, reader):
        Editable.load(self, reader)
        self.cells = [Cell(self.attrs, reader=reader) for i in range(self.num)]
        for cell in self.cells:
            cell.attrs.append(CellAttributes(reader=reader))


class LABL(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='LBAL')
        self.uint32('size_')
        self.names = []

    def load(self, reader):
        Editable.load(self, reader)
        assert self.magic == 'LBAL'
        offsets = []
        while True:
            offset = reader.readUInt32()
            if offset > self.size_:
                break
            offsets.append(offset)
        start = reader.tell()-4
        for offset in offsets:
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
        assert self.magic == 'RECN'
        self.cebk.load(reader)
        self.labl.load(reader)

    def save(self, writer=None):
        writer = Editable.save(self, writer)
        writer = self.cebk.save(writer)
        return writer
