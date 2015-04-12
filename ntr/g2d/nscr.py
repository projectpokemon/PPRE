
import array

from PIL import Image

from generic.editable import XEditable as Editable


class SCRN(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='NRCS')
        self.uint32('size_')
        self.uint16('width')
        self.uint16('height')
        self.uint16('format')
        self.uint16('type')
        self.uint32('datasize')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = array.array('H', reader.read(self.datasize))


class NSCR(Editable):
    def define(self):
        self.string('magic', length=4, default='RSCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=1)
        self.scrn = SCRN(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.scrn.load(reader)

    def get_image(self, cgr=None, clr=None):
        img = Image.new('RGBA', (self.scrn.width, self.scrn.height))
        if cgr is None:
            return img
        tiles = cgr.get_tiles()
        palettes = clr.get_palettes()
        pix = img.load()

        scr_x = scr_y = 0
        for tiledata in self.scrn.data:
            tile = tiles[tiledata & 0x3FF]
            if (tiledata >> 10) & 1:
                flip_y_factor = -1
            else:
                flip_y_factor = 1
            if (tiledata >> 11) & 1:
                flip_x_factor = -1
            else:
                flip_x_factor = 1
            palette = palettes[(tiledata >> 12) & 0xF]
            for sub_y in range(8)[::flip_y_factor]:
                for sub_x in range(8)[::flip_x_factor]:
                    val = tile[sub_y][sub_x]
                    if val:
                        pix[(scr_x+sub_x, scr_y+sub_y)] = palette[val]
                    else:
                        pix[(scr_x+sub_x, scr_y+sub_y)] = (0, 0, 0, 0)
            scr_x += 8
            if scr_x >= self.scrn.width:
                scr_x = 0
                scr_y += 8
                if scr_y >= self.scrn.height:
                    break
        return img
