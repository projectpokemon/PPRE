
import struct

from generic import Editable
from generic.collection import SizedCollection
from ntr.g3d.btx import TEX
from ntr.g3d.resdict import G3DResDict
from util import BinaryIO


class Node(Editable):
    FLAG_NO_TRANSLATE = 0x1
    FLAG_NO_ROTATE = 0x2
    FLAG_NO_SCALE = 0x4
    FLAG_NO_PIVOT = 0x8

    def define(self):
        self.uint16('flag_')
        for i in range(3):
            for j in range(3):
                self.uint16('rot_{0}{1}_fx16'.format(i, j))
        self.uint32('trans_x_fx32')
        self.uint32('trans_y_fx32')
        self.uint32('trans_z_fx32')
        self.uint16('pivot_a_fx16')
        self.uint16('pivot_b_fx16')
        self.uint32('scale_x_fx32', default=4096)
        self.uint32('scale_y_fx32', default=4096)
        self.uint32('scale_z_fx32', default=4096)
        self.uint32('inv_scale_x_fx32', default=4096)
        self.uint32('inv_scale_y_fx32', default=4096)
        self.uint32('inv_scale_z_fx32', default=4096)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.flag_ = reader.readUInt16()
        self.rot_00_fx16 = reader.readUInt16()
        if self.flag_ & self.FLAG_NO_TRANSLATE:
            self.trans_x_fx32 = 0
            self.trans_y_fx32 = 0
            self.trans_z_fx32 = 0
        else:
            self.trans_x_fx32 = reader.readUInt32()
            self.trans_y_fx32 = reader.readUInt32()
            self.trans_z_fx32 = reader.readUInt32()
        if self.flag_ & self.FLAG_NO_ROTATE:
            for i in range(3):
                for j in range(3):
                    setattr(self, 'rot_{0}{1}_fx16'.format(i, j), 0)
        elif self.flag_ & self.FLAG_NO_PIVOT:
            self.rot_01_fx16 = reader.readUInt16()
            self.rot_02_fx16 = reader.readUInt16()
            self.rot_10_fx16 = reader.readUInt16()
            self.rot_11_fx16 = reader.readUInt16()
            self.rot_12_fx16 = reader.readUInt16()
            self.rot_20_fx16 = reader.readUInt16()
            self.rot_21_fx16 = reader.readUInt16()
            self.rot_22_fx16 = reader.readUInt16()
        else:
            raise NotImplementedError('Cannot read pivots')

        if self.flag_ & self.FLAG_NO_SCALE:
            self.scale_x_fx32 = 4096
            self.scale_y_fx32 = 4096
            self.scale_z_fx32 = 4096
            self.inv_scale_x_fx32 = 4096
            self.inv_scale_y_fx32 = 4096
            self.inv_scale_z_fx32 = 4096
        else:
            self.scale_x_fx32 = reader.readUInt32()
            self.scale_y_fx32 = reader.readUInt32()
            self.scale_z_fx32 = reader.readUInt32()
            self.inv_scale_x_fx32 = reader.readUInt32()
            self.inv_scale_y_fx32 = reader.readUInt32()
            self.inv_scale_z_fx32 = reader.readUInt32()

    def save(self, writer):
        writer = BinaryIO.writer(writer)
        flag = self.flag
        writer.writeUInt16(flag)
        writer.writeUInt16(self.rot_00_fx16)
        if not (self.flag & self.FLAG_NO_TRANSLATE):
            writer.writeUInt32(self.trans_x_fx32)
            writer.writeUInt32(self.trans_y_fx32)
            writer.writeUInt32(self.trans_z_fx32)
        if not (self.flag & self.FLAG_NO_ROTATE):
            writer.writeUInt16(self.rot_01_fx16)
            writer.writeUInt16(self.rot_02_fx16)
            writer.writeUInt16(self.rot_10_fx16)
            writer.writeUInt16(self.rot_11_fx16)
            writer.writeUInt16(self.rot_20_fx16)
            writer.writeUInt16(self.rot_21_fx16)
            writer.writeUInt16(self.rot_22_fx16)
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
            writer.writeUInt32(self.scale_x_fx32)
            writer.writeUInt32(self.scale_y_fx32)
            writer.writeUInt32(self.scale_z_fx32)
            writer.writeUInt32(self.inv_scale_x_fx32)
            writer.writeUInt32(self.inv_scale_y_fx32)
            writer.writeUInt32(self.inv_scale_z_fx32)
        return writer

    @property
    def flag(self):
        flag = 0
        if not self.trans_x_fx32 and not self.trans_y_fx32 and\
                not self.trans_z_fx32:
            flag |= self.FLAG_NO_TRANSLATE
        for i in range(3):
            for j in range(3):
                if getattr(self, 'rot_{0}{1}_fx16'.format(i, j)):
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
            ofs, = struct.unpack(self.nodedict.data[i])
            self.reader.seek(start+ofs)
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
        self.materials = []
        self.shapes = []
        self.matrixes = []

    def load(self, reader):
        start = reader.tell()
        Editable.load(self, reader)

        self.nodes = []
        for i in range(self.num_nodes):
            nodedict = G3DResDict()
            nodedict.load(reader)
            self.nodes.append(Node(nodedict, reader=reader))  # Node

        self.sbc = []
        reader.seek(start+self.sbc_offset)
        for i in range(self.mat_offset-self.sbc_offset):
            self.sbc.append(reader.readUInt8())  # SBC

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
