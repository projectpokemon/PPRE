
import array
from cStringIO import StringIO
import itertools
import json

from PIL import Image

from generic.archive import ArchiveList
from generic.editable import XEditable as Editable
from util import BinaryIO


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
    """ DIM_SHAPES = {
        0: ((8, 8), (16, 16), (32, 32), (64, 64)),
        1: ((16, 8), (32, 8), (32, 16), (64, 32)),
        2: ((8, 16), (8, 32), (16, 32), (32, 64)),
    }"""

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
        return not self.is_rotscale and (self.rotparam & 0x8)

    @property
    def vertical_flip(self):
        return not self.is_rotscale and (self.rotparam & 0x10)


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

    @property
    def chunks(self):
        """Meta information for exported images

        When saving an image, use im.save(..., pnginfo=cell)

        """
        return [('tEXt', 'Comment\0'+self.to_json())]


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
        start = reader.tell()
        Editable.load(self, reader)
        self.cells = [Cell(self.attrs, reader=reader) for i in range(self.num)]
        for cell in self.cells:
            cell.attrs = [CellAttributes(reader=reader)
                          for i in range(cell.num)]
        if self.size_:
            reader.seek(start+self.size_)

    def save(self, writer):
        start = writer.tell()
        self.num = len(self.cells)
        writer = Editable.save(self, writer)
        for cell in self.cells:
            writer = cell.save(writer)
        for cell in self.cells:
            for attr in cell.attrs:
                writer = attr.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer


class LABL(Editable):
    def define(self, parent):
        self.parent = parent
        self.string('magic', length=4, default='LBAL')
        self.uint32('size_')
        self.names = []

    def load(self, reader):
        Editable.load(self, reader)
        assert self.magic == 'LBAL', 'Expected LBAL got '.format(self.magic)
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

    def save(self, writer):
        start = writer.tell()
        writer = Editable.save(self, writer)
        namewriter = BinaryIO()
        offsets = []
        for name in self.names:
            offsets.append(namewriter.tell())
            namewriter.write(name)
            namewriter.write(chr(0))
        for offset in offsets:
            writer.writeUInt32(offset)
        writer.write(namewriter.getvalue())
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer


class NCER(Editable, ArchiveList):
    extension = '.png'

    def define(self):
        self.string('magic', length=4, default='RECN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size_')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.cebk = CEBK(self)
        self.restrict('cebk')
        self.labl = LABL(self)
        self.restrict('labl')
        self._files = None

    def load(self, reader):
        Editable.load(self, reader)
        assert self.magic == 'RECN'
        self.cebk.load(reader)
        self.labl.load(reader)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        writer = self.cebk.save(writer)
        writer = self.labl.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer

    def get_image(self, id, cgr, clr):
        cell = self.cebk.cells[id]
        # maxX = min(cell.maxX for cell in self.cebk.cells)
        # maxY = min(cell.maxY for cell in self.cebk.cells)
        # minX = min(cell.minX for cell in self.cebk.cells)
        # minY = min(cell.minY for cell in self.cebk.cells)
        maxX = cell.maxX
        maxY = cell.maxY
        minX = cell.minX
        minY = cell.minY

        img = Image.new('RGBA', (maxX-minX+1, maxY-minY+1))
        tiles = cgr.get_tiles()
        palettes = clr.get_palettes()
        pix = img.load()

        for attr in cell.attrs:
            tile_id = attr.tileofs
            # apply flip outside too?
            if attr.vertical_flip:
                flip_y_factor = -1
            else:
                flip_y_factor = 1
            if attr.horizontal_flip:
                flip_x_factor = -1
            else:
                flip_x_factor = 1
            for scr_y in range(attr.y-minY, attr.y-minY+attr.height, 8)[::flip_y_factor]:
                for scr_x in range(attr.x-minX, attr.x-minX+attr.width, 8)[::flip_x_factor]:
                    tile = tiles[tile_id]
                    palette = palettes[attr.pal_id]
                    for sub_y, tile_y in enumerate(range(8)[::flip_y_factor]):
                        for sub_x, tile_x in enumerate(range(8)[::flip_x_factor]):
                            val = tile[tile_y][tile_x]
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
        if self._files is not None:
            return self._files
        try:
            cgr = self._cgr
            clr = self._clr
        except AttributeError:
            raise ValueError('No dependencies set. '
                             'Call update_dependencies(cgr, clr)')
        self._files = []
        for idx, cell in enumerate(self.cebk.cells):
            image = self.get_image(idx, cgr, clr)
            buffer = StringIO()
            image.save(buffer, format='PNG', pnginfo=cell)
            self._files.append(buffer.getvalue())
            buffer.close()
        return self._files

    def update_dependencies(self, cgr, clr):
        self._cgr = cgr
        self._clr = clr
        self._files = None

    def reset(self):
        # TODO: zero out self
        self.cebk.cells = []
        self._files = None
        try:
            self._cgr
            self._clr
        except AttributeError:
            raise ValueError('No dependencies set.'
                             'Call update_dependencies(cgr, clr)')

    def flush(self):
        """Build after an import_
        """
        try:
            cgr = self._cgr
            clr = self._clr
        except AttributeError:
            raise ValueError('No dependencies set.'
                             'Call update_dependencies(cgr, clr)')
        self.cebk.attrs = 1
        palettes = clr.get_palettes()
        changes_pal_ids = set()
        tiles = []
        for idx, data in enumerate(self._files):
            img = Image.open(StringIO(data))
            comment = img.info.get('Comment')
            img = img.convert('RGBA')
            pal_id = 0
            try:
                cell = self.cebk.cells[idx]
            except IndexError:
                cell = Cell(1)
                self.cebk.cells.append(cell)
                try:
                    info = json.loads(comment)
                    pal_id = info['pal_id']
                    cell.from_dict(json.loads(comment))
                except:
                    pass

            if pal_id not in changes_pal_ids:
                palettes[pal_id] = [(0xF8, 0xF8, 0xF8, 0)]
            palette = palettes[pal_id]
            pixels = img.load()

            # build some new attrs
            cell.attrs = []
            width, height = img.size
            scr_x = cell.minX
            scr_y = cell.minY
            while width > 0 or height > 0:
                # HACK: Currently using only 64x64 blocks
                attr = CellAttributes()
                attr.x = scr_x
                attr.y = scr_y
                attr.shape = 0
                attr.size_ = 3
                cell.attrs.append(attr)
                scr_x += 64
                scr_y += 64
                width -= 64
                height -= 64
            cell.maxX = scr_x
            cell.maxY = scr_y

            for attr in cell.attrs:
                tilestrip = []
                for img_y in range(attr.y-cell.minY,
                                   attr.y-cell.minY+attr.height, 8):
                    for img_x in range(attr.x-cell.minX,
                                       attr.x-cell.minX+attr.width, 8):
                        tile = []
                        for i in range(8):
                            tile.append([0]*8)
                        for sub_y in range(8):
                            for sub_x in range(8):
                                try:
                                    pix = pixels[img_x+sub_x, img_y+sub_y]
                                    if pix[3] < 0x80:
                                        tile[sub_y][sub_x] = 0
                                        continue
                                    color = (pix[0] & 0xF8, pix[1] & 0xF8,
                                             pix[2] & 0xF8, 255)
                                except:
                                    tile[sub_y][sub_x] = 0
                                    continue
                                try:
                                    index = palette.index(color, 1)
                                except:
                                    index = len(palette)
                                    if index >= 16:
                                        tile[sub_y][sub_x] = 0
                                        continue
                                        raise ValueError(
                                            'Cannot have more '
                                            'than 16 colors for image')
                                    changes_pal_ids.add(pal_id)
                                    palette.append(color)
                                tile[sub_y][sub_x] = index
                        tilestrip.append(tile)
                strip_len = len(tilestrip)
                # duplicate region check
                for tile_id in range(0, len(tiles)-strip_len):
                    if tiles[tile_id:tile_id+strip_len] == tilestrip:
                        attr.tileofs = tile_id
                        break
                else:
                    attr.tileofs = len(tiles)
                    tiles.extend(tilestrip)
        for pal_id in changes_pal_ids:
            clr.set_palette(pal_id, palettes[pal_id])
        cgr.set_tiles(tiles)
