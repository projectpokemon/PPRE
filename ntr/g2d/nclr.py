
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
