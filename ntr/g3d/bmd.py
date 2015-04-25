
import struct

from generic import Editable
from generic.collection import SizedCollection
from ntr.g3d.btx import TEX
from ntr.g3d.resdict import G3DResDict
from util import BinaryIO


class MaterialSet(Editable):
    def define(self):
        self.uint16('texmatdict_offset')
        self.uint16('palmatdict_offset')
        self.matdict = G3DResDict()
        self.texmatdict = G3DResDict()
        self.palmatdict = G3DResDict()
        self.materials = []
        self.tex_map = {}
        self.pal_map = {}

    def load(self, reader):
        start = reader.tell()
        Editable.load(self, reader)
        self.matdict.load(reader)
        reader.seek(start+self.texmatdict_offset)
        self.texmatdict.load(reader)
        reader.seek(start+self.palmatdict_offset)
        self.palmatdict.load(reader)

        self.materials = []
        self.tex_map = {}
        self.pal_map = {}

        for i in range(self.texmatdict.num):
            idx_ofs, idx_num, bound = struct.unpack('HBB', self.texmatdict.data[i])
            reader.seek((idx_ofs & 0xFFFF)+start)
            for j in range(idx_num):
                idx = reader.readUInt8()
                if idx in self.tex_map and not bound:
                    continue
                self.tex_map[idx] = i
        for i in range(self.palmatdict.num):
            idx_ofs, idx_num, bound = struct.unpack('HBB', self.palmatdict.data[i])
            reader.seek((idx_ofs & 0xFFFF)+start)
            for j in range(idx_num):
                idx = reader.readUInt8()
                if idx in self.pal_map and not bound:
                    continue
                self.pal_map[idx] = i
        for i in range(self.matdict.num):
            ofs, = struct.unpack('I', self.matdict.data[i])
            reader.seek(ofs+start)
            self.materials.append(Material(reader=reader))

    def save(self, writer):
        return writer


class Node(Editable):
    FLAG_NO_TRANSLATE = 0x1
    FLAG_NO_ROTATE = 0x2
    FLAG_NO_SCALE = 0x4
    FLAG_NO_PIVOT = 0x8
    FLAG_PIVOT_REVC = 0x200
    FLAG_PIVOT_REVD = 0x200

    def define(self):
        self.uint16('flag_')
        for i in range(3):
            for j in range(3):
                self.int16('rot_{0}{1}_fx16'.format(i, j),
                           default=int(i == j)*4096)
        self.int32('trans_x_fx32')
        self.int32('trans_y_fx32')
        self.int32('trans_z_fx32')
        self.int16('pivot_a_fx16')
        self.int16('pivot_b_fx16')
        self.int32('scale_x_fx32', default=4096)
        self.int32('scale_y_fx32', default=4096)
        self.int32('scale_z_fx32', default=4096)
        self.int32('inv_scale_x_fx32', default=4096)
        self.int32('inv_scale_y_fx32', default=4096)
        self.int32('inv_scale_z_fx32', default=4096)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.flag_ = reader.readUInt16()
        self.rot_00_fx16 = reader.readInt16()
        if self.flag_ & self.FLAG_NO_TRANSLATE:
            self.trans_x_fx32 = 0
            self.trans_y_fx32 = 0
            self.trans_z_fx32 = 0
        else:
            self.trans_x_fx32 = reader.readInt32()
            self.trans_y_fx32 = reader.readInt32()
            self.trans_z_fx32 = reader.readInt32()
        if self.flag_ & self.FLAG_NO_ROTATE:
            for i in range(3):
                for j in range(3):
                    setattr(self, 'rot_{0}{1}_fx16'.format(i, j),
                            int(i == j)*4096)
        elif self.flag_ & self.FLAG_NO_PIVOT:
            self.rot_01_fx16 = reader.readInt16()
            self.rot_02_fx16 = reader.readInt16()
            self.rot_10_fx16 = reader.readInt16()
            self.rot_11_fx16 = reader.readInt16()
            self.rot_12_fx16 = reader.readInt16()
            self.rot_20_fx16 = reader.readInt16()
            self.rot_21_fx16 = reader.readInt16()
            self.rot_22_fx16 = reader.readInt16()
        else:
            for i in range(3):
                for j in range(3):
                    setattr(self, 'rot_{0}{1}_fx16'.format(i, j),
                            int(i == j)*4096)
            self.pivot_a_fx16 = reader.readInt16()
            self.pivot_b_fx16 = reader.readInt16()
            pivot = (self.flag_ >> 4) & 0xf
            if self.flag_ & self.FLAG_PIVOT_REVC:
                pivoc_c = -self.pivot_b_fx16
            else:
                pivoc_c = self.pivot_b_fx16
            if self.flag_ & self.FLAG_PIVOT_REVD:
                pivoc_d = -self.pivot_a_fx16
            else:
                pivoc_d = self.pivot_a_fx16
            if pivot == 0:
                self.rot_11_fx16 = self.pivot_a_fx16
                self.rot_12_fx16 = self.pivot_b_fx16
                self.rot_21_fx16 = pivoc_c
                self.rot_22_fx16 = pivoc_d
            elif pivot == 4:
                self.rot_00_fx16 = self.pivot_a_fx16
                self.rot_02_fx16 = self.pivot_b_fx16
                self.rot_20_fx16 = pivoc_c
                self.rot_22_fx16 = pivoc_d
            elif pivot == 8:
                self.rot_00_fx16 = self.pivot_a_fx16
                self.rot_01_fx16 = self.pivot_b_fx16
                self.rot_10_fx16 = pivoc_c
                self.rot_11_fx16 = pivoc_d
            else:
                raise NotImplementedError('Pivot {0} is not supported'
                                          .format(pivot))

        if self.flag_ & self.FLAG_NO_SCALE:
            self.scale_x_fx32 = 4096
            self.scale_y_fx32 = 4096
            self.scale_z_fx32 = 4096
            self.inv_scale_x_fx32 = 4096
            self.inv_scale_y_fx32 = 4096
            self.inv_scale_z_fx32 = 4096
        else:
            self.scale_x_fx32 = reader.readInt32()
            self.scale_y_fx32 = reader.readInt32()
            self.scale_z_fx32 = reader.readInt32()
            self.inv_scale_x_fx32 = reader.readInt32()
            self.inv_scale_y_fx32 = reader.readInt32()
            self.inv_scale_z_fx32 = reader.readInt32()

    def save(self, writer):
        writer = BinaryIO.writer(writer)
        flag = self.flag
        writer.writeUInt16(flag)
        writer.writeInt16(self.rot_00_fx16)
        if not (self.flag & self.FLAG_NO_TRANSLATE):
            writer.writeInt32(self.trans_x_fx32)
            writer.writeInt32(self.trans_y_fx32)
            writer.writeInt32(self.trans_z_fx32)
        if not (self.flag & self.FLAG_NO_ROTATE):
            writer.writeInt16(self.rot_01_fx16)
            writer.writeInt16(self.rot_02_fx16)
            writer.writeInt16(self.rot_10_fx16)
            writer.writeInt16(self.rot_11_fx16)
            writer.writeInt16(self.rot_20_fx16)
            writer.writeInt16(self.rot_21_fx16)
            writer.writeInt16(self.rot_22_fx16)
        if not (self.flag & self.FLAG_NO_SCALE):
            try:
                self.inv_scale_x = 1/self.scale_x
            except ZeroDivisionError:
                self.inv_scale_x = 0.0
            try:
                self.inv_scale_y = 1/self.scale_y
            except ZeroDivisionError:
                self.inv_scale_y = 0.0
            try:
                self.inv_scale_z = 1/self.scale_z
            except ZeroDivisionError:
                self.inv_scale_z = 0.0
            writer.writeInt32(self.scale_x_fx32)
            writer.writeInt32(self.scale_y_fx32)
            writer.writeInt32(self.scale_z_fx32)
            writer.writeInt32(self.inv_scale_x_fx32)
            writer.writeInt32(self.inv_scale_y_fx32)
            writer.writeInt32(self.inv_scale_z_fx32)
        return writer

    @property
    def flag(self):
        flag = 0
        if not self.trans_x_fx32 and not self.trans_y_fx32 and\
                not self.trans_z_fx32:
            flag |= self.FLAG_NO_TRANSLATE
        for i in range(3):
            for j in range(3):
                if getattr(self, 'rot_{0}{1}_fx16'.format(i, j))\
                        != int(i == j)*4096:
                    break
            else:
                continue
            break
        else:
            flag |= self.FLAG_NO_ROTATE
        flag |= self.FLAG_NO_PIVOT
        if self.scale_x_fx32 == 4096 and self.scale_y_fx32 == 4096\
                and self.scale_z_fx32 == 4096:
            flag |= self.FLAG_NO_SCALE
            # TODO: make sure inv_scale match

    @flag.setter
    def flag(self, value):
        self.flag_ = value

    trans_x = Editable.fx_property('trans_x_fx32')
    trans_y = Editable.fx_property('trans_y_fx32')
    trans_z = Editable.fx_property('trans_z_fx32')
    pivot_a = Editable.fx_property('pivot_a_fx16')
    pivot_b = Editable.fx_property('pivot_b_fx16')
    scale_x = Editable.fx_property('scale_x_fx32')
    scale_y = Editable.fx_property('scale_y_fx32')
    scale_z = Editable.fx_property('scale_z_fx32')
    inv_scale_x = Editable.fx_property('inv_scale_x_fx32')
    inv_scale_y = Editable.fx_property('inv_scale_y_fx32')
    inv_scale_z = Editable.fx_property('inv_scale_z_fx32')
for i in range(3):
    for j in range(3):
        setattr(Node, 'rot_{0}{1}'.format(i, j),
                Editable.fx_property('rot_{0}{1}_fx16'.format(i, j)))


class NodeSet(object):
    def __init__(self):
        self.nodedict = G3DResDict()
        self.nodes = []

    def load(self, reader):
        start = reader.tell()
        self.nodedict.load(reader)
        self.nodes = []
        for i in range(self.nodedict.num):
            ofs, = struct.unpack('I', self.nodedict.data[i])
            reader.seek(start+ofs)
            self.nodes.append(Node(reader=reader))

    def save(self, writer):
        self.nodedict.num = len(self.nodes)
        self.nodedict.data = [chr(0)*4]*self.nodedict.num
        start = writer.tell()
        writer = self.nodedict.save(writer)
        for i in range(self.nodedict.num):
            self.nodedict.data[i] = struct.pack('I', writer.tell()-start)
            writer = self.nodes[i].save(writer)
        with writer.seek(start):
            writer = self.nodedict.save(writer)
        return writer


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
        self.nodes = NodeSet()
        self.sbc = []
        self.materials = MaterialSet()
        self.shapes = []
        self.matrixes = []

    def load(self, reader):
        start = reader.tell()
        Editable.load(self, reader)

        self.nodes.load(reader)
        assert self.nodes.nodedict.num == self.num_nodes

        self.sbc = []
        reader.seek(start+self.sbc_offset)
        for i in range(self.mat_offset-self.sbc_offset):
            self.sbc.append(reader.readUInt8())  # SBC

        reader.seek(start+self.mat_offset)
        self.materials.load(reader)
        assert self.materials.matdict.num == self.num_materials

        self.shapes = []
        reader.seek(start+self.shp_offset)
        for i in range(self.num_shapes):
            self.shapes.append(None)  # Shape

    def save(self, writer):
        start = writer.tell()
        writer = Editable.save(self, writer)

        writer = self.nodes.save(writer)

        ofs = writer.tell()-start
        with writer.seek(start+self.get_offset('sbc_offset')):
            writer.writeUInt32(ofs)
        for command in self.sbc:
            writer.writeUInt8(command)

        ofs = writer.tell()-start
        with writer.seek(start+self.get_offset('mat_offset')):
            writer.writeUInt32(ofs)

        ofs = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(ofs)
        return writer


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
        self.mdldict.num = len(self.models)
        writer = Editable.save(self, writer)
        writer = self.mdldict.save(writer)
        for i in range(self.mdldict.num):
            writer = self.models[i].save(writer)
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
