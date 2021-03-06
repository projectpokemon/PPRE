
import re

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

palette_2bpp = (0, 3, 2, 1)


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
                x = 2  # x = 1
                for tile_x in range(2):
                    tile = self.tiles[tile_y*2+tile_x][sub_y]
                    for sub_x in range(8)[::-1]:
                        if x > width*2:
                            break
                        """if (tile >> (sub_x*2)) & 0x3 == 1:
                            # HACK: BDF only supports 1bpp! Only keeping main
                            line |= 1
                        line <<= 1
                        x += 1
                        """
                        val = (tile >> (sub_x*2)) & 0x3
                        line |= palette_2bpp[val]
                        line <<= 2
                        x += 2
                line <<= -x % 8
                x += -x % 8
                lines.append('{line:0{fill}X}'.format(line=line, fill=x/4))
                y += 1
        return '\n'.join(lines)

    def set_line(self, y, width, line):
        tile_y = y/8
        sub_y = y % 8
        x = (width*2)-2
        line >>= -(width*2) % 8
        for tile_x in range(2):
            tile = 0
            for sub_x in range(8)[::-1]:
                if x < 0:
                    break
                val = palette_2bpp[(line >> x) & 0x3]
                # line >>= 2
                tile |= val << (sub_x*2)
                x -= 2
            self.tiles[tile_y*2+tile_x][sub_y] = tile

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
        self.uint8('cell_width', default=0x10)
        self.uint8('cell_height', default=0x10)
        self.uint8('ue', default=0x2)  # bit depth?
        self.uint8('uf', default=0x2)  # ?
        self.glyphs = []
        self.widths = []

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

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        self.num = len(self.glyphs)
        base_glyph = Glyph()
        self.footer_offset = base_glyph.get_size()*self.num+self.headersize
        writer = Editable.save(self, writer)
        writer = self.glyphs.save(writer)
        self.widths = [0]*self.num
        for i, glyph in enumerate(self.glyphs):
            self.widths[i] = width = glyph.get_bbox()[0]
            writer.writeUInt8(width)
        return writer

    def resize(self, num):
        self.glyphs.resize(num)
        new_widths = [0]*num
        old_num = len(self.widths)
        self.widths = self.widths+new_widths[old_num:]
        self.widths = self.widths[:num]

    def to_bdf(self):
        """Returns the contents of a BDF font file"""
        table, rtable = load_table()
        entries = {}
        for glyph_id, glyph in enumerate(self.glyphs):
            try:
                char = table[glyph_id+1].decode('unicode-escape')
                if char[:2] == '\\x':
                    char = chr(int(char[2], 16))
                ucode = ord(char)
            except:
                ucode = 0x8000+glyph_id
            # width, height, x_ofs, y_ofs = glyph.get_bbox()
            width = self.widths[glyph_id]
            entries[ucode] = """STARTCHAR U+{ucode:04X} ({glyph_id})
ENCODING {ucode}
SWIDTH 300 0
DWIDTH {width} 0
BBX {width} 16 0 0
BITMAP
{bitmap}
ENDCHAR
""".format(ucode=ucode, width=width, glyph_id=glyph_id,
                # height=height-2, x_ofs=x_ofs, y_ofs=y_ofs-2,
                bitmap=glyph.bdf_bitmap(width))

        bdf = """STARTFONT 2.3
FONT -ppre-pokemon-native--16-160-75-75
SIZE 16 75 75 2
FONTBOUNDINGBOX 16 16 0 0
BITS_PER_PIXEL 2
STARTPROPERTIES 3
FONT_ASCENT 16
FONT_DESCENT 0
ENDPROPERTIES
CHARS {num}
""".format(num=len(entries))
        for ucode in sorted(entries):
            bdf += entries[ucode]
        bdf += 'ENDFONT\n'
        return bdf

    def from_bdf(self, handle):
        """Loads a BDF font file"""
        try:
            reader = BinaryIO.reader(handle)
            assert reader.readline().split(' ')[0] == 'STARTFONT'
        except:
            raise ValueError('Expected BDF handle to be loaded')

        table, rtable = load_table()

        startchar_re = re.compile('^STARTCHAR U?\+?([0-9A-F]+)')
        bbox_re = re.compile('^BBX ([0-9]+) ([0-9]+) (-?[0-9]+) (-?[0-9]+)')
        encoding_re = re.compile('^ENCODING (?:-1 )?([0-9]+)')
        bits_re = re.compile('^BITS_?PER_?PIXEL_? (1|2|4|8|16|32)')
        size_re = re.compile('^SIZE [0-9]+ [0-9]+ [0-9]+ ([0-9]+)')
        bpp = 1

        while True:
            line = reader.readline()
            if line.startswith('CHARS'):
                num = int(line.strip('\n').split(' ')[1])
                break
            match = size_re.match(line)
            if match:
                bpp = int(match.group(1))
                continue

        entries = {}
        while num > 0:
            while True:
                line = reader.readline()
                match = startchar_re.match(line)
                if not match:
                    continue
                ucode = int(match.group(1), 16)
                break
            entries[ucode] = entry = Glyph()
            ecode = None
            width = height = None
            x_ofs = 0
            y_ofs = 0
            while True:
                line = reader.readline()
                if line.startswith('ENDCHAR'):
                    break
                if line.startswith('STARTCHAR'):
                    # WARNING: Overflowed
                    break
                match = encoding_re.match(line)
                if match:
                    ecode = int(match.group(1))
                    continue
                match = bits_re.match(line)
                if match:
                    bpp = int(match.group(1))
                    continue
                match = bbox_re.match(line)
                if match:
                    width = int(match.group(1))
                    x_ofs = int(match.group(3))
                    height = int(match.group(2))
                    y_ofs = int(match.group(4))
                if line.startswith('BITMAP'):
                    if width is None:
                        # WARNING: BBX not set
                        continue
                    if bpp != 2:
                        # WARNING: not 2bpp
                        continue
                    if x_ofs != 0:
                        # ???
                        pass
                    for y in range(16-height-y_ofs, 16):
                        line = reader.readline()
                        if line.startswith('ENDCHAR'):
                            break
                        entry.set_line(y, width, int(line, 16))
                    else:
                        continue
                    break
            num -= 1
        num = len(entries)
        for ucode in entries:
            if ucode & 0xF000 == 0x8000:
                num = max(ucode-0x7FFF, num)
        self.num = num
        self.glyphs = SizedCollection(Glyph().base_struct, length=num)
        for ucode in entries:
            if ucode & 0xF000 == 0x8000:
                glyph_id = ucode-0x8000
            else:
                glyph_id = rtable[unichr(ucode).encode('unicode-escape')]-1
            self.glyphs[glyph_id] = entries[ucode]._data

if __name__ == '__main__':
    import sys
    from pokemon import Game

    try:
        game = Game.from_workspace(sys.argv[1])
        command = sys.argv[2]
        assert command in ('--import', '--export')
        filename = sys.argv[3]
    except:
        print('Usage: {0} <workspace/> < --import| --export> <filename.bdf>'
              .format(sys.argv[0]))
        exit()
    font = Font(reader=game.font_archive.files[0])
    if command == '--export':
        with open(filename, 'w') as handle:
            handle.write(font.to_bdf())
    elif command == '--import':
        with open(filename) as handle:
            font.from_bdf(handle)
    else:
        raise NotImplementedError()
