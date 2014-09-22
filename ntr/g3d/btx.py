
from collections import namedtuple

from rawdb.generic.archive import Archive
from rawdb.util.io import BinaryIO


class TEX(Archive):
    def __init__(self, reader=None):
        self.magic = 'TEX0'
        self.endian = 0xFFFE
        self.texinfo = TexInfo()
        self.tex4x4info = TexInfo()
        self.palinfo = TexInfo()
        self.texdict = G3DResDict()
        self.paldict = G3DResDict()
