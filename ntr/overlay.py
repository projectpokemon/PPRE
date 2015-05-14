
from arm.elf import ELF
from generic.editable import XEditable as Editable


class Overlay(Editable):
    def define(self):
        self.uint32('id')
        self.uint32('address')
        self.uint32('size')
        self.uint32('bss_size')
        self.uint32('init_start')  # Pointer to the first initializer function.
        self.uint32('init_end')
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

    def to_binary_object(self, game):
        """Converts an overlay to an object file loaded at the proper offsets

        Parameters
        ----------
        game : Game
            Game to load overlays from

        Returns
        -------
        elf : ELF
            binary
        """
        elf = ELF()
        with game.open('overlays_dez/overlay_{0:04}.bin'.format(self.id))\
                as overlay:
            elf.add_binary(overlay, address=self.address)
        return elf


class OverlayTable(Editable):
    """For overarm9.bin"""
    def define(self, count):
        self.array('overlays', Overlay().base_struct, length=count)
