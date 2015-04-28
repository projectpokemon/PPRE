"""Sound Data Archive"""

from generic import Editable
from generic.archive import Archive
from util import BinaryIO


class SYMB(Editable):
    """SDAT Symbols

    These contain the "filenames" of the archive data.
    """
    record_names = ['SEQ', 'SEQARC', 'BANK', 'WAVEARC', 'PLAYER',
                    'GROUP', 'PLAYER2', 'STRM']

    def define(self, sdat):
        self.sdat = sdat
        self.string('magic', length=4, default='SYMB')
        self.uint32('size_')
        self.array('record_offsets', self.uint32, length=14)
        self.records = {}

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        self.records = {}
        for record_ofs, record_name in zip(self.record_offsets,
                                           self.record_names):
            if not record_ofs:
                continue
            reader.seek(start+record_ofs)
            num = reader.readUInt32()
            if record_name == 'SEQARC':
                offsets = []
                for i in range(num):
                    offsets.append(reader.readUInt32(), reader.readUInt32())
                entries = []
                for i, (offset, sub_offset) in enumerate(offsets):
                    reader.seek(start+offset)
                    name = reader.readString()
                    prefix = (record_name, name)
                    entries += self.load_entries(reader, start, prefix, num)
            else:
                entries = self.load_entries(reader, start, (record_name,), num)
            self.records[record_name] = entries

    @staticmethod
    def load_entries(reader, base_offset, prefix, num):
        offsets = []
        for i in range(num):
            offsets.append(reader.readUInt32())
        entries = []
        for i, offset in enumerate(offsets):
            if not offset:
                entries.append(prefix+(str(i),))
                continue
            reader.seek(base_offset+offset)
            entries.append(prefix+(reader.readString(),))
        return entries


class SDAT(Archive, Editable):
    """Sound Data Archive"""
    extension = ''  # filenames include their own extension

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
        self.fat = None  # FAT(self)
        self.info = None  # INFO(self)
        self.file = None  # FILE(self)

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
            if not block_ofs.block_offset:
                continue
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
