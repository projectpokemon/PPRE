
from generic.editable import XEditable as Editable


class CHAR(Editable):
    """Character information"""
    FORMAT_16BIT = 3
    FORMAT_256BIT = 4

    def define(self, cgr):
        self.cgr = cgr
        self.string('magic', length=4, default='RAHC')
        self.uint32('size_')
        self.uint16('width')
        self.uint16('height')
        self.uint32('format')
        self.uint32('depth')
        self.uint32('type')
        self.uint32('datasize')
        self.uint32('offset')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = reader.read(self.datasize)


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

    def load(self, reader):
        Editable.load(self, reader)
        self.char.load(reader)
        self.cpos.load(reader)
