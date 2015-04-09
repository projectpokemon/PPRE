
from generic.editable import XEditable as Editable


class Overlay(Editable):
    def define(self):
        self.uint32('id')
        self.uint32('address')
        self.uint32('size')
        self.uint32('bss_size')
        self.uint32('start')
        self.uint32('end')
        self.uint32('file_id')
        self.uint32('reserved')

    @property
    def compressed(self):
        return self.reserved & (1 << 24)

    @compressed.setter
    def compressed(self, value):
        if value:
            self.reserved |= 1 << 24
        else:
            self.reserved &= ~(1 << 24)


class OverlayTable(Editable):
    """For overarm9.bin"""
    def define(self, count):
        self.array('overlays', Overlay().base_struct, length=count)
