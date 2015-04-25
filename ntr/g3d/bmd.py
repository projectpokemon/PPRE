
from generic import Editable
from ntr.g3d.btx import TEX
from ntr.g3d.resdict import G3DResDict
from util import BinaryIO


class MDL(Editable):
    def define(self):
        self.string('magic', length=4, default='MDL0')
        self.uint32('size_')
        self.mdldict = G3DResDict()
        self.mdldict.sizeunit = 4
        self.models = []

    def load(self, reader):
        Editable.load(self, reader)
        self.mdldict.load(reader)
        self.models = []
        for idx in range(self.mdldict.num):
            # self.models.append(Model(reader=reader))
            pass

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        writer = self.mdldict.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer


class BMD(Editable):
    """3d Model container

    Attributes
    ----------
    mdl : MDL
        Model data
    tex : TEX
        Texture data
    """
    def define(self):
        self.string('magic', length=4, default='BMD0')
        self.uint16('endian', default=0xFEFF)
        self.uint16('version', default=0x2)
        self.uint32('size_')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=2)
        self.mdl = MDL()
        self.tex = TEX()

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        Editable.load(self, reader)
        assert self.magic == 'BMD0', 'Expected BMD0 got '.format(self.magic)
        block_offsets = []
        for i in range(self.numblocks):
            block_offsets.append(reader.readUInt32())
        reader.seek(start+block_offsets[0])
        self.mdl.load(reader)
        if self.numblocks > 1:
            reader.seek(start+block_offsets[1])
            self.tex.load(reader)
            self.tex.loaded = True
        else:
            self.tex.loaded = False

    def save(self, writer=None):
        if self.tex.loaded:
            self.numblocks = 2
        else:
            self.numblocks = 1
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        offset_offset = writer.tell()
        for i in self.numblocks:
            writer.writeUInt32(0)
        block_ofs = writer.tell()-start
        with writer.seek(offset_offset):
            writer.writeUInt32(block_ofs)
        writer = self.mdl.save(writer)
        if self.tex.loaded:
            block_ofs = writer.tell()-start
            with writer.seek(offset_offset+4):
                writer.writeUInt32(block_ofs)
            writer = self.tex.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer
