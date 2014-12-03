
from generic.archive import ArchiveList
from util.io import BinaryIO


class GARC(ArchiveList):
    """CTR Game Archive"""
    def __init__(self, reader=None):
        self.magic = 'CRAG'
        self.fato = FATO(self)
        self.fatb = FATB(self)
        self.fimb = FIMB(self)
        self.files = self.fimb.files
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        self.magic = reader.read(4)
        headersize = reader.readUInt32()
        u1 = reader.readUInt32()
        u2 = reader.readUInt32()
        u3 = reader.readUInt32()
        size = reader.readUInt32()
        u4 = reader.readUInt32()
        if headersize:
            reader.seek(start+headersize)
        self.fato.load(reader)
        self.fatb.load(reader)
        self.fimb.load(reader)
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        headersizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt32(0)
        writer.writeUInt32(0)
        writer.writeUInt32(0)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt32(0)
        size = writer.tell()-start
        with writer.seek(headersizeofs):
            writer.writeUInt32(size)
        writer = self.fato.save(writer)
        writer = self.fatb.save(writer)
        writer = self.fimb.save(writer)
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class FATO(object):
    """GARC FAT Offsets"""
    def __init__(self, garc):
        self.garc = garc
        self.magic = 'OTAF'
        self.offsets_ = []

    @property
    def num(self):
        return len(self.offsets)

    @property
    def offsets(self):
        return self.offsets_

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        num = reader.readUInt32()
        res = reader.readUInt32()

        self.offsets_ = [reader.readUInt32() for x in range(num)]
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt32(self.num)
        writer.writeUInt32(0)
        for offsets in self.offsets:
            writer.writeUInt32(offsets)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class FATB(object):
    """GARC FAT Blocks"""
    def __init__(self, garc):
        self.garc = garc
        self.magic = 'BTAF'
        self.entries_ = []

    @property
    def num(self):
        return len(self.garc.files)

    @property
    def entries(self):
        """List of slice objects that describe file image locations
        """
        entries = []
        start = 0
        for data in self.garc.fimb.files:
            stop = start+len(data)
            entries.append(slice(start, stop))
            start = stop+((-stop) % 4)
        return entries

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        num = reader.readUInt16()
        reader.readUInt16()

        self.entries_ = []
        for i in range(num):
            u0 = reader.readUInt32()
            start = reader.readUInt32()
            end = reader.readUInt32()
            size = reader.readUInt32()
            self.entries_.append(slice(start, end))
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt32(self.num)
        writer.writeUInt32(0)
        for entry in self.entries:
            writer.writeUInt32(0)
            writer.writeUInt32(entry.start)
            writer.writeUInt32(entry.stop)
            writer.writeUInt32(entry.stop-entry.start)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class FIMB(object):
    """GARC File Image Blocks"""
    def __init__(self, garc):
        self.garc = garc
        self.magic = 'BMIF'
        self.files = []

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        data = reader.read(size-8)
        self.files.extend([data[entry]
                           for entry in self.garc.fatb.entries_])
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        data = []
        for fdata, entry in zip(self.files, self.garc.fatb.entries):
            total = len(data)
            if entry.start > total:
                data += '\x00'*(entry.start-total)
            data[entry] = fdata
        writer.write(''.join(data))
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer
