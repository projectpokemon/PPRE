
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
        # attr0
        self.int16('y', width=8)
        self.uint16('is_rotscale', width=1)
        self.uint16('is_scalevis', width=1)
        self.uint16('mode', width=2)
        self.uint16('mosaic', width=1)
        self.uint16('palformat', width=1)
        self.uint16('shape', width=2)
        # attr1
        self.int16('x', width=9)
        self.uint16('rotparam', width=5)
        self.uint16('size_', width=2)
        # attr2
        self.uint16('tileofs', width=10)
        self.uint16('z_index', width=2)
        self.uint16('pal_id', width=3)

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
    def disabled(self):
        return not self.is_rotscale and self.is_scalevis

    @property
    def scale(self):
        return 2 if self.is_rotscale and self.is_scalevis else 1

    @property
    def horizontal_flip(self):
        return self.is_rotscale and (self.rotparam & 0x8)

    @property
    def vertical_flip(self):
        return self.is_rotscale and (self.rotparam & 0x10)


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
