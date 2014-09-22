
from rawdb.generic.archive import Archive
from rawdb.util.io import BinaryIO


class NARC(Archive):
    def __init__(self, reader=None):
        self.magic = 'NARC'
        self.endian = 0xFFFE
        self.version = 0x100
        self.numblocks = 3
        self.fatb = FATB(self)
        self.fntb = FNTB(self)
        self.fimg = FIMG(self)
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        self.endian = reader.readUInt16()
        self.version = reader.readUInt16()
        size = reader.readUInt32()
        headersize = reader.readUInt16()
        numblocks = reader.readUInt16()
        if headersize:
            reader.seek(start+headersize)
        self.fatb.load(reader)
        self.fntb.load(reader)
        self.fimg.load(reader)
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        writer.writeUInt16(self.endian)
        writer.writeUInt16(self.version)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        headersizeofs = writer.tell()
        writer.writeUInt16(0)
        writer.writeUInt16(self.numblocks)
        size = writer.tell()-start
        with writer.seek(headersizeofs):
            writer.writeUInt16(size)
        writer = self.fatb.save(writer)
        writer = self.fntb.save(writer)
        writer = self.fimg.save(writer)
        writer.writeUInt32(0)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer
