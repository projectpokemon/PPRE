
from collections import namedtuple
import struct

from rawdb.generic.archive import Archive
from rawdb.ntr.g3d.resdict import G3DResDict
from rawdb.util.io import BinaryIO


def log2(x):
    """Integer log2"""
    return x.bit_length()-1


class TexInfo(object):
    INFO_TEX = 0
    INFO_TEX4X4 = 1
    INFO_PAL = 2

    def __init__(self, tex, infotype=0):
        self.tex = tex
        self.vramkey = 0
        self.infotype = infotype

    def load(self, reader):
        self.vramkey = reader.readUInt32()
        self._datasize = reader.readUInt16()
        if self.infotype != TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Runtime-loaded
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Padding, always 0x8
        self._dataofs = reader.readUInt32()
        if self.infotype == TexInfo.INFO_TEX4X4:
            self._paldataofs = reader.readUInt32()
            self._datasize <<= 2
        else:
            self._datasize <<= 3

    def save(self, writer=None):
        """
        When writing the general structure, it saves offsets
        to unknown values. It is the duty of the parent to
        fill these in
        """
        writer = writer if writer is not None else BinaryIO()
        writer.writeUInt32(self.vramkey)
        self._datasize_ofs = writer.tell()
        writer.writeUInt16(0)  # datasize
        if self.infotype != TexInfo.INFO_PAL:
            self._lookupofs_ofs = writer.tell()
            writer.writeUInt16(0)
        writer.writeUInt16(0)
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs_ofs = writer.tell()
            writer.writeUInt16(0)
        writer.writeUInt16(8)
        self._dataofs_ofs = writer.tell()
        writer.writeUInt32(0)
        if self.infotype == TexInfo.INFO_TEX4X4:
            writer.writeUInt32(0)
        return writer


TexParam = namedtuple('TexParam', 'ofs width height format color0')
PalParam = namedtuple('PalParam', 'ofs count4')


class TEX(Archive):
    def __init__(self, reader=None):
        self.magic = 'TEX0'
        self.endian = 0xFFFE
        self.texinfo = TexInfo(self)
        self.tex4x4info = TexInfo(self, TexInfo.INFO_TEX4X4)
        self.palinfo = TexInfo(self, TexInfo.INFO_PAL)
        self.texdict = G3DResDict()
        self.texdict.sizeunit = 8
        self.paldict = G3DResDict()
        self.texparams = []
        self.palparams = []
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        self.texinfo.load(reader)
        self.tex4x4info.load(reader)
        self.palinfo.load(reader)
        # Build dicts
        reader.seek(start+self.texinfo._lookupofs)
        self.texdict.load(reader)
        self.texparams = []
        for i in xrange(self.texdict.num):
            imgParam, extra = struct.unpack('II', self.texdict.data[i])
            self.texparams.append(TexParam((imgParam & 0xFFFF) << 3,
                                           8 << ((imgParam >> 20) & 0x7),
                                           8 << ((imgParam >> 23) & 0x7),
                                           (imgParam >> 26) & 0x7,
                                           (imgParam >> 29) & 0x1))
        reader.seek(start+self.palinfo._lookupofs)
        self.paldict.load(reader)
        self.palparams = []
        for i in xrange(self.paldict.num):
            offset, flag = struct.unpack('HH', self.paldict.data[i])
            self.palparams.append(PalParam(offset << 3, flag))
        # Read data.
        reader.seek(start+self.texinfo._dataofs)
        self.texdata = reader.read(self.texinfo._datasize)
        reader.seek(start+self.palinfo._dataofs)
        self.paldata = reader.read(self.palinfo._datasize)
        # TODO 4x4
        if size:
            reader.seek(start+size)

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        start = writer.tell()
        writer.write(self.magic)
        size_ofs = writer.tell()
        writer.writeUInt32(0)
        writer = self.texinfo.save(writer)
        writer = self.tex4x4info.save(writer)
        writer = self.palinfo.save(writer)

        writer.writeAlign(4)
        ofs = writer.tell()-start
        with writer.seek(self.texinfo._lookupofs_ofs):
            writer.writeUInt16(ofs)
        writer = self.texdict.save(writer)

        writer.writeAlign(4)
        ofs = writer.tell()-start
        with writer.seek(self.palinfo._lookupofs_ofs):
            writer.writeUInt16(ofs)
        writer = self.paldict.save(writer)

        writer.writeAlign(8)
        ofs = writer.tell()-start
        with writer.seek(self.texinfo._dataofs_ofs):
            writer.writeUInt32(ofs)  # texinfo dataofs
        datastart = writer.tell()
        for i in xrange(self.texdict.num):
            texparam = self.texparams[i]
            writer.writeUInt32((texparam.ofs >> 3) |
                               ((log2(texparam.width) >> 3) << 20) |
                               ((log2(texparam.height) >> 3) << 23) |
                               (texparam.format << 26) |
                               (texparam.color0 << 29))
            writer.writeUInt32(0)
        writer.writeAlign(8)
        size = writer.tell()-datastart
        with writer.seek(self.texinfo._datasize_ofs):
            writer.writeUInt16(size >> 3)  # texinfo datasize

        writer.writeAlign(8)
        ofs = writer.tell()-start
        with writer.seek(self.palinfo._dataofs_ofs):
            writer.writeUInt32(ofs)  # palinfo dataofs
        datastart = writer.tell()
        for i in xrange(self.texdict.num):
            param = self.palparams[i]
            writer.writeUInt16(param.ofs)
            writer.writeUInt16(param.count4)
        writer.writeAlign(8)
        size = writer.tell()-datastart
        with writer.seek(self.palinfo._datasize_ofs):
            writer.writeUInt16(size >> 3)  # palinfo datasize

        return writer
