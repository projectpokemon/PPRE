
from PIL import Image

from atomic.atomic_struct import SIMULATING_PLACEHOLDER
from generic import Editable
from generic.collection import SizedCollection
from util import BinaryIO


palette = (
    (0xFF, 0xFF, 0xFF, 0),
    (0, 0, 0, 255),
    (0x88, 0x88, 0x88, 255),
    (0xCC, 0xCC, 0xCC, 255),
)


class Glyph(Editable):
    def define(self):
        tile = self.array(SIMULATING_PLACEHOLDER, self.uint16, length=8)
        self.array('tiles', lambda x: tile, length=4)

    def to_image(self):
        img = Image.new('RGBA', (16, 16))
        pix = img.load()

        pix_x = pix_y = 0
        for tile_y in range(2):
            for sub_y in range(8):
                pix_x = 0
                for tile_x in range(2):
                    tile = self.tiles[tile_y*2+tile_x][sub_y]
                    for sub_x in range(8)[::-1]:
                        pix[pix_x, pix_y] = palette[(tile >> (sub_x*2)) & 0x3]
                        pix_x += 1
                pix_y += 1
        return img


class Font(Editable):
    """Pokemon Font Glyph Table
    """
    def define(self):
        self.uint32('headersize', default=0x10)
        self.uint32('footer_offset')
        self.uint32('num')
        self.uint8('cell_width')
        self.uint8('cell_height')
        self.uint8('ue')  # baseline from bottom?
        self.uint8('uf')  # bit depth?
        self.glyphs = []
        self.widths = []  # Footer array

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        self.glyphs = []
        # TODO: glyph reading
        self.glyphs = SizedCollection(Glyph().base_struct, length=self.num)
        self.glyphs.load(reader)
        self.widths = []
        reader.seek(start+self.footer_offset)
        for i in range(self.num):
            self.widths.append(reader.readUInt8())
