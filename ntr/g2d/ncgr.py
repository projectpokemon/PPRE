
from generic.editable import XEditable as Editable

from PIL import Image


def default_palette():
    return [chr(c)*3+chr(255) for c in range(256)]


class CHAR(Editable):
    """Character information"""
    FORMAT_16BIT = 3
    FORMAT_256BIT = 4

    def define(self, cgr):
        self.cgr = cgr
        self.string('magic', length=4, default='RAHC')
        self.uint32('size_')
        self.uint16('height')
        self.uint16('width')
        self.uint32('format')
        self.uint32('depth')
        self.uint32('type')
        self.uint32('datasize')
        self.uint32('offset')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = reader.read(self.datasize)

    def get_tiles(self):
        tiles = []
        if self.format == self.FORMAT_16BIT:
            subwidth = 4
        elif self.format == self.FORMAT_256BIT:
            subwidth = 8
        for tile_id in range(self.datasize/subwidth/8):
            tile = []
            for tile_y in range(8):
                tile.append([])
                for tile_x in range(subwidth):
                    val = ord(self.data[tile_id*8*subwidth+
                                        tile_y*subwidth+tile_x])
                    if self.format == self.FORMAT_16BIT:
                        tile[tile_y].append(val & 0xF)
                        tile[tile_y].append(val >> 0x4)
                    elif self.format == self.FORMAT_256BIT:
                        tile[tile_y].append(val)
            tiles.append(tile)
        return tiles

    def set_tiles(self, tiles):
        self.data = ''
        if self.format == self.FORMAT_16BIT:
            subwidth = 4
        elif self.format == self.FORMAT_256BIT:
            subwidth = 8
        for tile in tiles:
            for tile_y in range(8):
                for tile_x in range(subwidth):
                    if self.format == self.FORMAT_16BIT:
                        val = tile[tile_y][tile_x*2]
                        val |= tile[tile_y][tile_x*2+1] << 4
                    elif self.format == self.FORMAT_256BIT:
                        val = tile[tile_y][tile_x]
                    self.data += chr(val)
        old_datasize = self.datasize
        self.datasize = len(self.data)
        self.size_ += self.datasize-old_datasize

    def get_pixels(self, width=None, height=None):
        """pixels = [[[]]]
        subx = suby = 0
        blockx = blocky = 0
        for c in self.data:
            val = ord(c)
            if self.format == self.FORMAT_16BIT:
                pixels[blocky][blockx][suby].append(val & 0xF)
                pixels[blocky][blockx][suby].append(val >> 0x4)
                subx += 2
            elif self.format == self.FORMAT_256BIT:
                pixels[blocky][blockx][suby].append(val)
                subx += 1
            if subx == 8:
                subx = 0
                suby += 1
                if suby == 8:
                    blockx += 1
                    if blockx == 8:
                        blockx = 0
                        blocky += 1
                        pixels.append([[[]]])
                    else:
                        pixels[blocky].append([[]])
                else:
                    pixels[blocky][blockx].append([])"""
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        pixels = []
        if self.format == self.FORMAT_16BIT:
            subwidth = 4
        elif self.format == self.FORMAT_256BIT:
            subwidth = 8
        for blocky in range(height):
            for suby in range(8):
                for blockx in range(width):
                    for subx in range(subwidth):
                        val = ord(self.data[(blocky*width*8*subwidth)+
                                            (blockx*8*subwidth)+
                                            (suby*subwidth)+subx])
                        if self.format == self.FORMAT_16BIT:
                            pixels.append(val & 0xF)
                            pixels.append(val >> 0x4)
                        elif self.format == self.FORMAT_256BIT:
                            pixels.append(val)
        return pixels


class CPOS(Editable):
    """Character Position"""
    def define(self, cgr):
        self.cgr = cgr
        self.string('magic', length=4, default='SOPC')
        self.uint32('size_')
        self.uint16('posx')
        self.uint16('posy')
        self.uint16('width')
        self.uint16('height')


class NCGR(Editable):
    """2D Character Graphics
    """
    def define(self):
        self.string('magic', length=4, default='RGCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x101)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.char = CHAR(self)
        self.cpos = CPOS(self)
        self.palette = default_palette()

    def load(self, reader):
        Editable.load(self, reader)
        self.char.load(reader)
        if self.numblocks > 1:
            self.cpos.load(reader)

    def get_image(self, width=None, height=None):
        data = ''
        if width is None:
            width = self.char.width
        else:
            width >>= 3
        if height is None:
            height = self.char.height
        else:
            height >>= 3
        for pix in self.char.get_pixels(width, height):
            data += self.palette[pix]
        return Image.frombytes('RGBA', (width*8, height*8), data)

    def get_tiles(self):
        return self.char.get_tiles()

    def set_tiles(self, tiles):
        self.char.set_tiles(tiles)
