
import array

from PIL import Image

from generic.editable import XEditable as Editable


class PLTT(Editable):
    """Palette information"""
    FORMAT_16BIT = 3
    FORMAT_256BIT = 4

    def define(self, clr):
        self.clr = clr
        self.string('magic', length=4, default='PLTT')  # not reversed
        self.uint32('size_')
        self.uint32('format')
        self.uint32('extended')
        self.uint32('datasize')
        self.uint32('offset')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = array.array('H', reader.read(self.datasize))

    def save(self, writer):
        writer = Editable.save(self, writer)
        writer.write(self.data.tostring())
        return writer

    def get_palettes(self):
        palettes = []
        if self.format == self.FORMAT_16BIT:
            num = 16
        elif self.format == self.FORMAT_256BIT:
            num = 256
        start = 0
        for pal_id in range(len(self.data)/num):
            palette = []
            for i in range(num):
                val = self.data[start+i]
                palette.append((((val >> 0) & 0x1f) << 3,
                               ((val >> 5) & 0x1f) << 3,
                               ((val >> 10) & 0x1f) << 3,
                               255))
            start += num
            palettes.append(palette)
        return palettes

    def get_palette(self, pal_id, transparent=True):
        palette = []
        if self.format == self.FORMAT_16BIT:
            num = 16
        elif self.format == self.FORMAT_256BIT:
            num = 256
        start = pal_id*num
        for i in range(num):
            if not num and transparent:
                palette.append(chr(0)*4)
                continue
            val = self.data[start+i]
            palette.append(chr(((val >> 0) & 0x1f) << 3) +
                           chr(((val >> 5) & 0x1f) << 3) +
                           chr(((val >> 10) & 0x1f) << 3) +
                           chr(255))
        return palette

    def set_palette(self, pal_id, palette):
        """

        Parameters
        ----------
        pal_id : int
        palette : list of tuple
            List of 4-/3-int-tuple colors
        """
        if self.format == self.FORMAT_16BIT:
            num = 16
        elif self.format == self.FORMAT_256BIT:
            num = 256
        start = pal_id*num*2
        for i in range(num):
            r, g, b = palette[i*3:i*3+3]
            self.data[start+i] = ((r >> 3) |
                                  (g >> 3 << 5) |
                                  (b >> 3 << 10))


class NCLR(Editable):
    """2d color information
    """
    def define(self):
        self.string('magic', length=4, default='RLCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x101)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=1)
        self.pltt = PLTT(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.pltt.load(reader)

    def save(self, writer=None):
        writer = Editable.save(self, writer)
        writer = self.pltt.save(writer)
        return writer

    def get_palette(self, pal_id=0, transparent=True):
        return self.pltt.get_palette(pal_id, transparent)

    def get_palettes(self):
        return self.pltt.get_palettes()

    def set_palette(self, pal_id, palette):
        return self.pltt.set_palette(pal_id, palette)
