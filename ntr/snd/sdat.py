"""Sound Data Archive"""

from generic import Editable
from generic.archive import Archive
from util import BinaryIO


class SDAT(Archive, Editable):
    """Sound Data Archive"""
    def define(self):
        self.string('magic', length=4, default='SDAT')
        self.uint16('endian', default=0xFEFF)
        self.uint16('version', default=0x0001)
        self.uint32('size_')
        self.uint16('headersize')
        self.uint16('numblocks', default=4)
        block_ofs = Editable()
        block_ofs.uint32('block_offset')
        block_ofs.uint32('block_size')
        block_ofs.freeze()
        self.array('block_offsets', block_ofs.base_struct, length=8)
        self.symb = SYMB(self)
        self.fat = FAT(self)
        self.info = INFO(self)
        self.file = FILE(self)

    @property
    def files(self):
        return dict(zip(self.symb.entries, self.file.files))

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        assert self.magic == 'SDAT'
        for block_ofs, block in zip(self.block_offsets, [
                self.symb, self.fat, self.info, self.file]):
            reader.seek(start+block_ofs.block_offset)
            block.load(reader)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        for block_ofs, block in zip(self.block_offsets, [
                self.symb, self.fat, self.info, self.file]):
            block_ofs.block_offset = writer.tell()-start
            writer = block.save(writer)
            writer.writeAlign(4)
            block_ofs.block_size = writer.tell()-start-block_ofs.block_offset
        with writer.seek(start):
            writer = Editable.save(self, writer)
        return writer
