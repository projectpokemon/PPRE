
from collections import namedtuple

from atomic import AtomicStruct
from generic.archive import ArchiveList
from generic import Editable
from util.io import BinaryIO


class NARC(ArchiveList):
    def __init__(self, reader=None):
        self.magic = 'NARC'
        self.endian = 0xFFFE
        self.version = 0x102
        self.numblocks = 3
        self.fatb = FATB(self)
        self.fntb = FNTB(self)
        self.fimg = FIMG(self)
        self.files = self.fimg.files
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
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


class FATB(object):
    def __init__(self, narc):
        self.narc = narc
        self.magic = 'BTAF'
        self.entries_ = []

    @property
    def num(self):
        return len(self.narc.files)

    @property
    def entries(self):
        """List of slice objects that describe file image locations
        """
        entries = []
        start = 0
        for data in self.narc.fimg.files:
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
        for i in xrange(num):
            self.entries_.append(slice(reader.readUInt32(),
                                       reader.readUInt32()))
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt16(self.num)
        writer.writeUInt16(0)
        for entry in self.entries:
            writer.writeUInt32(entry.start)
            writer.writeUInt32(entry.stop)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class FNTB(object):
    def __init__(self, narc):
        self.narc = narc
        self.magic = 'BTNF'

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        writer.writeUInt32(4)
        writer.writeUInt32(0x10000)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class FIMG(object):
    def __init__(self, narc):
        self.narc = narc
        self.magic = 'GMIF'
        self.files = []

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        data = reader.read(size-8)
        self.files.extend([data[entry]
                           for entry in self.narc.fatb.entries_])

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        sizeofs = writer.tell()
        writer.writeUInt32(0)
        data = []
        for fdata, entry in zip(self.files, self.narc.fatb.entries):
            total = len(data)
            if entry.start > total:
                data += '\x00'*(entry.start-total)
            data[entry] = fdata
        writer.write(''.join(data))
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt32(size)
        return writer


class NARC(ArchiveList, Editable):
    def __init__(self, reader=None):
        Editable.__init__(self)
        self.string('magic', length=4, default='NARC')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x102)
        self.uint32('size_')
        self.uint16('headersize')
        self.uint16('numblocks', default=3)
        self.fatb = FATB(self)
        self.fntb = FNTB(self)
        self.fimg = FIMG(self)
        self.freeze()
        if reader is not None:
            self.load(reader)

    @property
    def files(self):
        return self.fimg.files

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        AtomicStruct.load(self, reader)
        self.fatb.load(reader)
        self.fntb.load(reader)
        self.fimg.load(reader)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        writer = self.fatb.save(writer)
        writer = self.fntb.save(writer)
        writer = self.fimg.save(writer)
        writer.writeAlign(4)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer

    def resize(self, num):
        """Changes the number of files in the NARC. This needs to be done
        before freely addressing later file entries

        Parameters
        ----------
        num : int
            Number to increase/decrease to
        """
        while len(self) < num:
            self.add()
        self.fimg.files = self.files[:num]


class FATB(Editable):
    def __init__(self, narc):
        AtomicStruct.__init__(self)
        self.narc = narc
        self.entries_ = []
        self.string('magic', length=4, default='BTAF')
        self.uint32('size_')
        self.uint16('num')
        self.uint16('u0')
        self.freeze()

    @property
    def num(self):
        return len(self.narc.files)

    @property
    def entries(self):
        """List of slice objects that describe file image locations
        """
        entries = []
        start = 0
        for data in self.narc.fimg.files:
            stop = start+len(data)
            entries.append(slice(start, stop))
            start = stop+((-stop) % 4)
        return entries

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        AtomicStruct.load(self, reader)
        for i in xrange(self._data.num):
            self.entries_.append(slice(reader.readUInt32(),
                                       reader.readUInt32()))

    def save(self, writer):
        start = writer.tell()
        self._data.num = self.num
        writer = Editable.save(self, writer)
        for entry in self.entries:
            writer.writeUInt32(entry.start)
            writer.writeUInt32(entry.stop)
        writer.writeAlign(4)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer


class LazyFiles(list):
    def __init__(self, handle, entries):
        self.offset = handle.tell()
        self.entries = entries


class FIMG(Editable):
    def __init__(self, narc):
        AtomicStruct.__init__(self)
        self.narc = narc
        self.files = []
        self.string('magic', length=4, default='GMIF')
        self.uint32('size_')
        self.freeze()

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        AtomicStruct.load(self, reader)
        data = reader.read(self.size_-8)
        self.files.extend([data[entry]
                           for entry in self.narc.fatb.entries_])

    def save(self, writer):
        start = writer.tell()
        writer = Editable.save(self, writer)
        rel = writer.tell()
        for file_id, entry in enumerate(self.narc.fatb.entries):
            writer.writePadding(entry.start+rel)
            writer.write(self.files[file_id])
        writer.writeAlign(4)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer
