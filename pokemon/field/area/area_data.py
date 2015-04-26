
from generic import Editable


class AreaData(Editable):
    def define(self):
        self.uint16('u0')
        self.uint16('texture_idx')
        self.uint16('u4', default=0xFFFF)
        self.uint8('u6', default=0)
        self.uint8('is_outdoors')
