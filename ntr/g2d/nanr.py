
from generic import Editable
from ntr.g2d.ncer import LABL


class AnimationFrame(Editable):
    def define(self):
        self.uint32('data_offset')
        self.uint16('frames')
        self.uint16('u6')


class AnimationSequence(Editable):
    def define(self):
        self.uint16('num_frames')
        self.uint16('start_idx')
        self.uint32('type')
        self.uint32('mode')
        self.uint32('frame_ofs')


class ABNK(Editable):
    def define(self, anr):
        self.anr = anr
        self.string('magic', length=4, default='KNBA')
        self.uint32('size_')
        self.uint16('num_seq')
        self.uint16('num_frames')
        self.uint32('seq_ofs')
        self.uint32('frame_ofs')
        self.uint32('data_offset')
        self.uint32('u18')
        self.uint32('u1c')


class NANR(Editable):
    """2d Animations
    """
    def define(self):
        self.string('magic', length=4, default='RNAN')
        self.uint16('endian', default=0xFEFF)
        self.uint16('version', default=0x100)
        self.uint32('size_')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=3)
        self.abnk = ABNK(self)
        self.labl = LABL(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.abnk.load(reader)
        # self.labl.load(reader)

