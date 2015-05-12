
from generic import Editable
from util import BinaryIO


class Font(Editable):
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
        self.widths = []
        reader.seek(start+self.footer_offset)
        for i in range(self.num):
            self.widths.append(reader.readUInt8())
