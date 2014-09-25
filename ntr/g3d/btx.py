
from collections import namedtuple

from rawdb.generic.archive import Archive
from rawdb.ntr.g3d.resdict import G3DResDict
from rawdb.util.io import BinaryIO


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
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs_ofs = writer.tell()
        writer.writeUInt16(8)
        self._dataofs_ofs = writer.tell()
        writer.writeUInt32(0)
        if self.infotype == TexInfo.INFO_TEX4X4:
            writer.writeUInt32(0)


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
        reader = BinaryIO()
        start = reader.tell()
        self.magic = reader.read(4)
        size = reader.readUInt32()
        self.texinfo.load(reader)
        self.tex4x4info.load(reader)
        self.palinfo.load(reader)
        # Build dicts
        reader.seek(start+self.texinfo._lookupofs)
        self.texdict.load(reader)
        reader.seek(start+self.palinfo._lookupofs)
        self.paldict.load(reader)
        # Read data.
        reader.seek(start+self.texinfo._dataofs)
        for i in xrange(self.texdict.num):
            imgParam = reader.readUInt32()
            extra = reader.readUInt32()
            self.texparams.append(TexParam((imgParam & 0xFFFF) << 3,
                                           8 << ((imgParam >> 20) & 0x7),
                                           8 << ((imgParam >> 23) & 0x7),
                                           (imgParam >> 26) & 0x7,
                                           (imgParam >> 29) & 0x1))
        reader.seek(start+self.palinfo._dataofs)
        for i in xrange(self.paldict.num):
            offset = reader.readUInt16()
            flag = reader.readUInt16()
            self.palparams.append(PalParam(offset << 3, flag))
        # TODO 4x4
        if size:
            reader.seek(start+size)
