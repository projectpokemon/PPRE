
from PIL import Image

from generic import Editable
from util import BinaryIO
from util.colors import color_gen


class Permission(Editable):
    def define(self, game):
        self.game = game
        self.uint16('perm', width=8)
        self.uint16('flags', width=8)


class MapObject(Editable):
    def define(self, game):
        self.game = game
        self.uint32('object_id')
        self.uint16('u4')
        self.int16('x')
        self.uint32('u8')
        self.uint16('uc')
        self.int16('y')
        self.uint32('u10')
        self.uint32('u14')
        self.uint32('u18')
        self.uint32('u1c')
        self.uint32('u20')
        self.uint32('u24')
        self.uint32('u28')
        self.uint32('u2c')


class SizedCollection(Editable):
    def define(self, entry, total_size):
        self.array('entries', entry.base_struct,
                   length=total_size/entry.get_size())


class BDHC(Editable):
    def define(self, game):
        self.uint32('u0')


class LandDataMap(Editable):
    def define(self, game):
        self.game = game
        self.uint32('permission_size')
        self.uint32('objects_size')
        self.uint32('bmd_size')
        self.uint32('bdhc_size')
        self.uint16('magic', default=0x1234)
        self.uint16('ublock1_size')

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        Editable.load(self, reader)
        self.block1 = reader.read(self.ublock1_size)
        """entry_size = Permission(self.game).get_size()
        # self.permissions = [Permission(self.game, reader=reader)
        #                     for i in range(self.permission_size/entry_size)]
        self.permissions = Editable()
        self.permissions.array('entries', Permission(self.game).base_struct,
                               length=self.permission_size/entry_size)
        self.permissions.freeze()
        self.permissions.load(reader)
        entry_size = MapObject(self.game).get_size()
        self.objects = [MapObject(self.game, reader=reader)
                        for i in range(self.objects_size/entry_size)]"""
        self.permissions = SizedCollection(Permission(self.game),
                                           self.permission_size)
        self.permissions.load(reader)
        self.objects = SizedCollection(MapObject(self.game),
                                       self.objects_size)
        self.objects.load(reader)
        self.bmd = reader.read(self.bmd_size)  # TODO later
        self.bdhc = BDHC(self.game)
        self.bdhc.load(reader)

    def get_perm_image(self):
        res = 8
        image = Image.new('RGBA', (0x20*res, 0x20*res))
        pix = image.load()
        idx = 0
        colors = {}
        gen = color_gen()
        for y in range(0x20):
            for x in range(0x20):
                entry = self.permissions.entries[idx]
                perm = entry.perm
                try:
                    color = colors[perm]
                except KeyError:
                    color = next(gen)
                    colors[perm] = color
                if entry.flags & 0x80:
                    color = tuple(c/4 for c in color[:3])+(255,)
                for sub_y in range(res):
                    for sub_x in range(res):
                        pix[x*res+sub_x, y*res+sub_y] = color
                idx += 1
        for obj in self.objects.entries:
            color = (255, 255, 255, 255)
            x = obj.x + 0x10
            y = obj.y + 0x10
            for i in range(res-2):
                pix[x*res+i+2, y*res+res-1] = color
                pix[x*res+res-1, y*res+i+2] = color
        return image
