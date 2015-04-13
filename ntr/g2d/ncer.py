
import array
from cStringIO import StringIO
import itertools

from PIL import Image

from generic.archive import Archive
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
        self.uint16('is_scalevis', width=1)  # self.disabled, self.scale
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
        self.uint16('pal_id', width=4)

    @property
    def width(self):
        return {self.SHAPE_SQUARE: [8, 16, 32, 64],
                self.SHAPE_HORIZONTAL: [16, 32, 32, 64],
                self.SHAPE_VERTICAL: [8, 8, 16, 32]
                }.get(self.shape)[self.size_] * self.scale

    @property
    def height(self):
        return {self.SHAPE_SQUARE: [8, 16, 32, 64],
                self.SHAPE_HORIZONTAL: [8, 8, 16, 32],
                self.SHAPE_VERTICAL: [16, 32, 32, 64]
                }.get(self.shape)[self.size_] * self.scale

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


class NCER(Editable, Archive):
    extension = '.png'

    def define(self):
        self.string('magic', length=4, default='RECN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.cebk = CEBK(self)
        self.labl = LABL(self)
        self._files = {}

    def load(self, reader):
        Editable.load(self, reader)
        assert self.magic == 'RECN'
        self.cebk.load(reader)
        self.labl.load(reader)

    def save(self, writer=None):
        writer = Editable.save(self, writer)
        writer = self.cebk.save(writer)
        return writer

    def get_image(self, id, cgr, clr):
        maxX = min(cell.maxX for cell in self.cebk.cells)
        maxY = min(cell.maxY for cell in self.cebk.cells)
        minX = min(cell.minX for cell in self.cebk.cells)
        minY = min(cell.minY for cell in self.cebk.cells)
        img = Image.new('RGBA', (maxX-minX+1, maxY-minY+1))
        tiles = cgr.get_tiles()
        palettes = clr.get_palettes()
        pix = img.load()
        cell = self.cebk.cells[id]

        for attr in cell.attrs:
            tile_id = attr.tileofs
            # apply flip outside too?
            for scr_y in range(attr.y-minY, attr.y-minY+attr.height, 8):
                for scr_x in range(attr.x-minX, attr.x-minX+attr.width, 8):
                    tile = tiles[tile_id]
                    if attr.vertical_flip:
                        flip_y_factor = -1
                    else:
                        flip_y_factor = 1
                    if attr.horizontal_flip:
                        flip_x_factor = -1
                    else:
                        flip_x_factor = 1
                    palette = palettes[attr.pal_id]
                    for sub_y in range(8)[::flip_y_factor]:
                        for sub_x in range(8)[::flip_x_factor]:
                            val = tile[sub_y][sub_x]
                            try:
                                if val:
                                    pix[(scr_x+sub_x, scr_y+sub_y)] = palette[val]
                                elif 0:
                                    pix[(scr_x+sub_x, scr_y+sub_y)] = (0, 0, 0, 0)
                            except IndexError:
                                continue
                    tile_id += 1
        return img

    @property
    def files(self):
        if self._files:
            return self._files
        try:
            cgr = self._cgr
            clr = self._clr
        except AttributeError:
            raise ValueError('No dependencies set.'
                             'Call update_dependencies(cgr, clr)')
        for idx, (name, cell) in enumerate(zip(self.labl.names,
                                               self.cebk.cells)):
            image = self.get_image(idx, cgr, clr)
            buffer = StringIO()
            image.save(buffer, format='PNG')
            self._files[name] = buffer.getvalue()
            buffer.close()
        return self._files

    def update_dependencies(self, cgr, clr):
        self._cgr = cgr
        self._clr = clr
        self._files = {}
