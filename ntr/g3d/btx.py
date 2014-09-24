
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
        self._datasize = reader.readUInt16() << 3
        if self.infotype != TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Runtime-loaded
        if self.infotype == TexInfo.INFO_PAL:
            self._lookupofs = reader.readUInt16()
        reader.readUInt16()  # Padding, always 0x8
        self._dataofs = reader.readUInt32()
        if self.infotype == TexInfo.INFO_TEX4X4:
            self._paldataofs = reader.readUInt32()

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

    def load(self, reader):
        reader = BinaryIO()
        self.texinfo.load(reader)
