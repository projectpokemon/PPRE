
from generic.editable import XEditable as Editable

from PIL import Image


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
        self.data = reader.read(self.datasize)

    def get_palette(self, pal_id, transparent=True):
        palette = []
        if self.format == self.FORMAT_16BIT:
            num = 16
        elif self.format == self.FORMAT_256BIT:
            num = 256
        start = pal_id*num*2
        for i in range(num):
            if not num and transparent:
                palette.append(chr(0)*4)
                continue
            val = ord(self.data[start+i*2]) | \
                (ord(self.data[start+i*2+1]) << 8)
            palette.append(chr(((val >> 0) & 0x1f) << 3) +
                           chr(((val >> 5) & 0x1f) << 3) +
                           chr(((val >> 10) & 0x1f) << 3) +
                           chr(255))
        return palette


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

    def get_palette(self, pal_id=0, transparent=True):
        return self.pltt.get_palette(pal_id, transparent)
