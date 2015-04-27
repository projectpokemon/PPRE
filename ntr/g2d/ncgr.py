
import array

from PIL import Image

from generic import Editable
from util.io import BinaryIO


def default_palette():
    return [(c, c, c, 255) for c in range(16)*16]


class CHAR(Editable):
    """Character information"""
    FORMAT_16BIT = 3
    FORMAT_256BIT = 4
    ENCRYPT_MULT = 0x41c64e6d
    ENCRYPT_CARRY = 0x6073
    TYPE_LINEAR = 1

    def define(self, cgr):
        self.cgr = cgr
        self.string('magic', length=4, default='RAHC')
        self.uint32('size_')
        self.uint16('height')
        self.uint16('width')
        self.uint32('format', default=self.FORMAT_16BIT)
        self.uint32('depth')
        self.uint32('type')
        self.uint32('datasize')
        self.uint32('offset')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = reader.read(self.datasize)
        if self.cgr.encryption != NCGR.ENCRYPTION_NONE:
            self.decrypt(self.cgr.encryption)

    def save(self, writer):
        old_datasize = self.datasize
        if self.cgr.encryption != NCGR.ENCRYPTION_NONE:
            self.encrypt(self.cgr.encryption)
        self.datasize = len(self.data)
        self.size_ += self.datasize-old_datasize
        writer = Editable.save(self, writer)
        writer.write(self.data)
        return writer

    def encrypt(self, encryption):
        """Applies encryption/decryption to the sprite.

        Each call toggles its encrypted state, so calling it twice will
        bring it back to its original state.
        """
        if encryption is NCGR.ENCRYPTION_NONE:
            return
        enc_data = array.array('H', self.data)
        if encryption == NCGR.ENCRYPTION_REVERSE:
            enc_data = enc_data[::-1]
        dec_data = array.array('H')
        key = enc_data[0]
        for val in enc_data:
            dec_data.append(val ^ (key & 0xFFFF))
            key *= self.ENCRYPT_MULT
            key += self.ENCRYPT_CARRY
        self.data = dec_data.tostring()
    decrypt = encrypt

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

    def get_tile(self, tileofs):
        if self.format == self.FORMAT_16BIT:
            subwidth = 4
        elif self.format == self.FORMAT_256BIT:
            subwidth = 8
        tile = []
        for tile_y in range(8):
            tile.append([])
            for tile_x in range(subwidth):
                val = ord(self.data[tileofs+tile_y*subwidth+tile_x])
                if self.format == self.FORMAT_16BIT:
                    tile[tile_y].append(val & 0xF)
                    tile[tile_y].append(val >> 0x4)
                elif self.format == self.FORMAT_256BIT:
                    tile[tile_y].append(val)
        return tile

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
        else:
            raise ValueError('Unknown format: {0}'.format(self.format))
        if self.type == self.TYPE_LINEAR:
            data_idx = 0
            for suby in range(height*8):
                for subx in range(width*4):
                    val = ord(self.data[data_idx])
                    if self.format == self.FORMAT_16BIT:
                        pixels.append(val & 0xF)
                        pixels.append(val >> 0x4)
                    elif self.format == self.FORMAT_256BIT:
                        pixels.append(val)
                    data_idx += 1
            return pixels
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

    def set_pixels(self, pixels, width, height):
        data = array.array('B')
        if self.format == self.FORMAT_16BIT:
            subwidth = 4
        elif self.format == self.FORMAT_256BIT:
            subwidth = 8
        else:
            raise ValueError('Unknown format: {0}'.format(self.format))
        if self.type == self.TYPE_LINEAR:
            for pix_idx in range(width*height*8*subwidth):
                if self.format == self.FORMAT_16BIT:
                    data.append(pixels[pix_idx*2] |
                                (pixels[pix_idx*2+1] << 4))
                elif self.format == self.FORMAT_256BIT:
                    data.append(pixels[pix_idx])
        else:
            for blocky in range(height):
                for suby in range(8):
                    for blockx in range(width):
                        for subx in range(subwidth):
                            pix_idx = ((blocky*width*8*subwidth) +
                                       (blockx*8*subwidth) +
                                       (suby*subwidth)+subx)
                            if self.format == self.FORMAT_16BIT:
                                data.append(pixels[pix_idx*2] |
                                            (pixels[pix_idx*2+1] << 4))
                            elif self.format == self.FORMAT_256BIT:
                                data.append(pixels[pix_idx])
        self.data = data.tostring()


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
    ENCRYPTION_NONE = 0
    ENCRYPTION_REVERSE = 1
    ENCRYPTION_FORWARDS = 2

    EDIT_NONE = 0
    EDIT_ANY = 1
    ADD_ONLY = 2

    def define(self, encryption=ENCRYPTION_NONE):
        self.string('magic', length=4, default='RGCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x101)
        self.uint32('size_')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.char = CHAR(self)
        self.cpos = CPOS(self)
        self.palette = default_palette()
        self.encryption = encryption

    def load(self, reader):
        Editable.load(self, reader)
        assert self.magic == 'RGCN', 'Expected RGCN got '.format(self.magic)
        self.char.load(reader)
        if self.numblocks > 1:
            self.cpos.load(reader)
            self.cpos.loaded = True
        else:
            self.cpos.loaded = False

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        writer = self.char.save(writer)
        if self.cpos.loaded:
            writer = self.cpos.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer

    def get_image(self, width=None, height=None, transparent=True):
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
            if not pix and transparent:
                data += chr(0)*4
            else:
                data += ''.join(map(chr, self.palette[pix]))
        return Image.frombytes('RGBA', (width*8, height*8), data)

    def set_image(self, img, clr, modify_palette=EDIT_ANY, pal_id=0):
        img = img.convert('RGBA')
        if modify_palette == self.EDIT_ANY:
            palette = [(0xF8, 0xF8, 0xF8, 0)]
        else:
            palette = clr.get_palettes()[pal_id]
        pixels = []
        width, height = img.size
        for pix in img.getdata():
            if pix[3] < 0x80:
                pixels.append(0)
                continue
            color = (pix[0] & 0xF8, pix[1] & 0xF8,
                     pix[2] & 0xF8, 255)
            try:
                index = palette.index(color, 1)
            except:
                if modify_palette is self.EDIT_NONE:
                    raise ValueError('Some colors do not exist'
                                     ' in current palette')
                index = len(palette)
                if index >= 16:
                    if modify_palette is self.ADD_ONLY:
                        last = palette[-1]
                        index = palette.index(last, 1)
                        if last == len(palette)-1:
                            raise ValueError('Cannot have more than 16 colors')
                        palette[index] = color
                    else:
                        raise ValueError('Cannot have more than 16 colors')
                else:
                    palette.append(color)
            pixels.append(index)
        self.char.set_pixels(pixels, width, height)

    def get_tiles(self):
        return self.char.get_tiles()

    def get_tile(self, tileofs):
        return self.char.get_tile(tileofs)

    def set_tiles(self, tiles):
        self.char.set_tiles(tiles)
