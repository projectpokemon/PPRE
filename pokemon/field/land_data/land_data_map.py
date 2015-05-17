
from PIL import Image

from generic import Editable
from generic.collection import SizedCollection, Collection2d
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
        # x, y, z may be fixed point with 0x10000 as a denominator
        self.int16('fine_x')  # 0 when two wide
        self.int16('x')
        self.int16('fine_z')
        self.int16('z')  # Calling this Z to keep consistent with 2d maps
        self.int16('fine_y')  # 0 when 2 long, 0xc0000 when 2 long down??
        self.int16('y')
        # rots are not used (potentially not implemented?)
        self.int32('rot1_fx')
        self.int32('rot2_fx')
        self.int32('rot3_fx')
        # scales are only known to be 4096.0
        self.int32('scale_x_fx', default=4096)
        self.int32('scale_z_fx', default=4096)
        self.int32('scale_y_fx', default=4096)
        self.uint32('u28')
        self.uint32('u2c')


class BDHC(Editable):
    def define(self, game):
        self.uint32('u0')


class LandDataMap(Editable):
    def define(self, game):
        self.game = game
        self.uint32('permission_size', default=0x800)
        self.uint32('objects_size')
        self.uint32('bmd_size')
        self.uint32('bdhc_size')
        if game.is_hgss():
            self.uint16('magic', default=0x1234)
            self.uint16('ublock1_size')

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        Editable.load(self, reader)
        if self.game.is_hgss():
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
        entry = Permission(self.game)
        # TODO: non-fixed w/h
        self.permissions = Collection2d(entry.base_struct, 0x20, 0x20)
        self.permissions.load(reader)
        entry = MapObject(self.game)
        self.objects = SizedCollection(
            entry.base_struct, self.objects_size/entry.get_size())
        self.objects.load(reader)
        self.bmd = reader.read(self.bmd_size)  # TODO later
        self.bdhc = reader.read(self.bdhc_size)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        if self.game.is_hgss():
            writer.write(self.block1)
            self.ublock1_size = len(self.block1)
        writer = self.permissions.save(writer)
        self.permission_size = self.permissions.get_size()
        writer = self.objects.save(writer)
        self.objects_size = self.objects.get_size()
        writer.write(self.bmd)
        self.bmd_size = len(self.bmd)
        writer.write(self.bdhc)
        self.bdhc_size = len(self.bdhc)
        with writer.seek(start):
            Editable.save(self, writer)
        return writer

    def get_perm_image(self, res=8):
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
        color = (0xaa, 0xaa, 0xaa, 255)
        for y in range(0, 0x20, 4):
            for x in range(0, 0x20, 4):
                cross_iter = range(2-res/2, res/2, 2)
                for sub_y in cross_iter:
                    x_iter = [0] if sub_y else cross_iter
                    for sub_x in x_iter:
                        try:
                            pix[x*res+sub_x, y*res+sub_y] = color
                        except:
                            pass
        for obj in self.objects.entries:
            color = (255, 255, 255, 255)
            x = obj.x + 0x10
            y = obj.y + 0x10
            for i in range(res-2):
                try:
                    pix[x*res+i+2, y*res+res-1] = color
                    pix[x*res+res-1, y*res+i+2] = color
                except:
                    pass  # Don't bother with objects off-map
        return image
