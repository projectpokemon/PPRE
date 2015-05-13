
from PIL import Image

from atomic.atomic_struct import SIMULATING_PLACEHOLDER
from pokemon.msgdata.msg import load_table
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

    def bdf_bitmap(self, width):
        # width, height, x_ofs, y_ofs = self.get_bbox()
        lines = []
        y = 0
        for tile_y in range(2):
            for sub_y in range(8):
                """if y < 16-height:
                    y += 1
                    continue
                elif y > 16-y_ofs:
                    break"""
                line = 0
                x = 1
                for tile_x in range(2):
                    tile = self.tiles[tile_y*2+tile_x][sub_y]
                    for sub_x in range(8)[::-1]:
                        if x > width:
                            break
                        if (tile >> (sub_x*2)) & 0x3 == 1:
                            # HACK: BDF only supports 1bpp! Only keeping main
                            line |= 1
                        line <<= 1
                        x += 1
                line <<= -x % 8
                x += -x % 8
                lines.append('{line:0{fill}X}'.format(line=line, fill=x/4))
                y += 1
        return '\n'.join(lines)

    def get_bbox(self):
        """Returns the bounding region of the Glyph

        Returns
        -------
        width : int
        height : int
        x : int
        y : int
        """
        min_x = min_y = 16
        max_x = max_y = 0
        y = 0
        for tile_y in range(2):
            for sub_y in range(8):
                x = 0
                for tile_x in range(2):
                    tile = self.tiles[tile_y*2+tile_x][sub_y]
                    for sub_x in range(8)[::-1]:
                        val = (tile >> (sub_x*2)) & 0x3
                        if val != 0:
                            min_x = min(x, min_x)
                            min_y = min(y, min_y)
                            max_x = max(x, max_x)
                            max_y = max(y, max_y)
                        x += 1
                y += 1
        if min_x == min_y == 16 and max_x == max_y == 0:
            return 0, 0, 0, 2
        return (max_x-min_x+1, max_y-min_y+1, min_x, min_y)


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

    def to_bdf(self):
        table = load_table()
        entries = {}
        for glyph_id, glyph in enumerate(self.glyphs):
            try:
                char = table[glyph_id+1].decode('unicode-escape')
                if char[:2] == '\\x':
                    char = chr(int(char[2], 16))
            except:
                ucode = 0
            # width, height, x_ofs, y_ofs = glyph.get_bbox()
            width = self.widths[glyph_id]
            ucode = ord(char)
            entries[ucode] = """STARTCHAR U+{ucode:04X}
ENCODING {ucode}
SWIDTH 300 0
DWIDTH {width} 0
BBX {width} 16 0 0
BITMAP
{bitmap}
ENDCHAR
""".format(ucode=ucode, width=width,
                # height=height-2, x_ofs=x_ofs, y_ofs=y_ofs-2,
                bitmap=glyph.bdf_bitmap(width))

        bdf = """STARTFONT 2.1
FONT -ppre-pokemon-native--16-160-75-75
SIZE 16 75 75
FONTBOUNDINGBOX 16 16 0 0
STARTPROPERTIES 2
FONT_ASCENT 16
FONT_DESCENT 0
ENDPROPERTIES
CHARS {num}
""".format(num=len(entries))
        for ucode in sorted(entries):
            bdf += entries[ucode]
        bdf += 'ENDFONT\n'
        return bdf
