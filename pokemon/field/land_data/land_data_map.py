
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
        """
        # x, y, z may be fixed point with 0x10000 as a denominator
        self.uint16('u4')  # 0 when two wide
        self.int16('x')
        self.uint16('u8')
        self.int16('z')  # Calling this Z to keep consistent with 2d maps
        self.uint16('uc')  # 0 when 2 long, 0xc0000 when 2 long down??
        self.int16('y')
        self.uint32('u10')
        self.uint32('u14')
        self.uint32('u18')
        self.uint32('u1c')
        self.uint32('u20')
        self.uint32('u24')
        self.uint32('u28')
        self.uint32('u2c')"""
        self.int32('x_fx')
        self.int32('z_fx')
        self.int32('y_fx')
        self.int32('rot1')
        self.int32('rot2')
        self.int32('rot3')
        self.int32('scale_x_fx', default=4096)
        self.int32('scale_z_fx', default=4096)
        self.int32('scale_y_fx', default=4096)
        self.uint32('u28')
        self.uint32('u2c')

    def get_x(self):
        return self.x_fx/65536.0 + 0x10

    def get_z(self):
        return self.z_fx/65536.0 + 0x10

    def get_y(self):
        return self.y_fx/65536.0 + 0x10


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
            x = MapObject.get_x(obj)
            y = MapObject.get_y(obj)
            for i in range(res-2):
                pix[x*res+i+2, y*res+res-1] = color
                pix[x*res+res-1, y*res+i+2] = color
        return image
