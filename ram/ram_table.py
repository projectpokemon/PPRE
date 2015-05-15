
class RAMTable(object):
    ARM_ID = -1

    def __init__(self):
        self.overlay_id = None
        self.address = None
        self.table_class = None
        self.num_entries = None

    def get(self, game):
        inst = self.table_class(num=self.num_entries)
        with self.get_overlay(game) as handle:
            inst.load(handle=handle, address=self.address)
        return inst

    def get_overlay(self, game):
        if self.overlay_id is self.ARM_ID:
            return game.open('arm9.dec.bin')
        return game.open('overlayz_dez',
                         'overlay_{0:04}.bin'.format(self.overlay_id)
                         )
