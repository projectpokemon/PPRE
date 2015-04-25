
from generic import Editable
from ntr.g3d.btx import TEX
from ntr.g3d.resdict import G3DResDict
from util import BinaryIO


class Model(Editable):
    def define(self):
        self.uint32('size_')
        self.uint32('sbc_offset')
        self.uint32('mat_offset')
        self.uint32('shp_offset')
        self.uint32('matrix_offset')
        self.uint8('sbc_type')
        self.uint8('scale')
        self.uint8('tex_mode')
        self.uint8('num_nodes')
        self.uint8('num_materials')
        self.uint8('num_shapes')
        self.uint8('mtx_start')
        self.uint8('pad17', default=0)
        self.uint32('pos_scale_fx32')
        self.uint32('inv_pos_scale_fx32')
        self.uint16('num_vertex')
        self.uint16('num_polygon')
        self.uint16('num_triangle')
        self.uint16('num_quad')
        self.uint16('box_x_fx16')
        self.uint16('box_y_fx16')
        self.uint16('box_z_fx16')
        self.uint16('box_w_fx16')
        self.uint16('box_h_fx16')
        self.uint16('box_d_fx16')
        self.uint32('box_scale_fx32')
        self.uint32('inv_box_scale_fx32')
        self.nodes = []
        self.sbc = []
        self.materials = []
        self.shapes = []
        self.matrixes = []

    def load(self, reader):
        start = reader.tell()
        Editable.load(self, reader)

        self.nodes = []
        for i in range(self.num_nodes):
            self.nodes.append(None)  # Node

        self.sbc = []
        reader.seek(start+self.sbc_offset)
        for i in range(self.mat_offset-self.sbc_offset):
            self.sbc.append(None)  # SBC

        self.materials = []
        reader.seek(start+self.mat_offset)
        for i in range(self.num_materials):
            self.materials.append(None)  # Material

        self.shapes = []
        reader.seek(start+self.shp_offset)
        for i in range(self.num_shapes):
            self.shapes.append(None)  # Shape

    def save(self, writer):
        start = writer.tell()
        writer = Editable.save(self, writer)


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
            self.models.append(Model(reader=reader))

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
        for i in range(self.numblocks):
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
