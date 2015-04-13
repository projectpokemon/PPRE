
import array
import colorsys
import itertools

from PIL import Image

from generic.editable import XEditable as Editable
from util import BinaryIO


class SCRN(Editable):
    def define(self, scr):
        self.scr = scr
        self.string('magic', length=4, default='NRCS')
        self.uint32('size_')
        self.uint16('width')
        self.uint16('height')
        self.uint16('format')
        self.uint16('type')
        self.uint32('datasize')
        self.data = ''

    def load(self, reader):
        Editable.load(self, reader)
        self.data = array.array('H', reader.read(self.datasize))

    def save(self, writer):
        old_datasize = self.datasize
        self.datasize = len(self.data)*2
        self.size_ += self.datasize-old_datasize
        writer = Editable.save(self, writer)
        writer.write(self.data.tostring())
        return writer


class NSCR(Editable):
    EDIT_NONE = 0
    EDIT_ANY = 1
    ADD_ONLY = 2
    compressable = True

    def define(self):
        self.string('magic', length=4, default='RSCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size_')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=1)
        self.scrn = SCRN(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.scrn.load(reader)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        start = writer.tell()
        writer = Editable.save(self, writer)
        writer = self.scrn.save(writer)
        size = writer.tell()-start
        with writer.seek(start+self.get_offset('size_')):
            writer.writeUInt32(size)
        return writer

    def get_image(self, cgr=None, clr=None):
        img = Image.new('RGBA', (self.scrn.width, self.scrn.height))
        if cgr is None:
            return img
        tiles = cgr.get_tiles()
        palettes = clr.get_palettes()
        pix = img.load()

        scr_x = scr_y = 0
        for tiledata in self.scrn.data:
            tile = tiles[tiledata & 0x3FF]
            if (tiledata >> 10) & 1:
                flip_y_factor = -1
            else:
                flip_y_factor = 1
            if (tiledata >> 11) & 1:
                flip_x_factor = -1
            else:
                flip_x_factor = 1
            palette = palettes[(tiledata >> 12) & 0xF]
            for sub_y in range(8)[::flip_y_factor]:
                for sub_x in range(8)[::flip_x_factor]:
                    val = tile[sub_y][sub_x]
                    if val:
                        pix[(scr_x+sub_x, scr_y+sub_y)] = palette[val]
                    else:
                        pix[(scr_x+sub_x, scr_y+sub_y)] = (0, 0, 0, 0)
            scr_x += 8
            if scr_x >= self.scrn.width:
                scr_x = 0
                scr_y += 8
                if scr_y >= self.scrn.height:
                    break
        return img

    def get_target_image(self):
        img = Image.new('RGBA', (self.scrn.width, self.scrn.height))
        pix = img.load()
        scr_x = scr_y = 0
        for tiledata in self.scrn.data:
            tile_id = tiledata & 0x3FF
            if (tiledata >> 10) & 1:
                flip_y_factor = -1
            else:
                flip_y_factor = 1
            if (tiledata >> 11) & 1:
                flip_x_factor = -1
            else:
                flip_x_factor = 1
            color = colorsys.hsv_to_rgb(((tiledata >> 12) & 0xF)/16.0, 1, 0.5)
            color = (int(color[0]*255), int(color[1]*255),
                     int(color[2]*255), 255)
            if tile_id:
                for sub_y in range(8)[::flip_y_factor]:
                    for sub_x in range(8)[::flip_x_factor]:
                        pix[(scr_x+sub_x, scr_y+sub_y)] = color
            scr_x += 8
            if scr_x >= self.scrn.width:
                scr_x = 0
                scr_y += 8
                if scr_y >= self.scrn.height:
                    break
        return img

    def set_image(self, img, cgr, clr, modify_screen=EDIT_NONE,
                  modify_tiles=EDIT_ANY, modify_palette=ADD_ONLY):
        """

        Parameters
        ----------
        modify_screen : {EDIT_NONE, EDIT_ANY}
            If EDIT_NONE, make no changes to this screen
            If EDIT_ANY, freely make changes to this screen.
        modify_tiles : {EDIT_NONE, EDIT_ANY, ADD_ONLY}
            If EDIT_NONE, find matching existing tiles. modify_screen must
                be EDIT_ANY
            If EDIT_ANY, freely change the tiles
            If ADD_ONLY, add tiles to the end only. modify_screen must be
                EDIT_ANY
        modify_palette : {EDIT_NONE, EDIT_ANY, ADD_ONLY}
            If EDIT_NONE, use the existing palette and make no changes.
            If EDIT_ANY, freely change this palette
            If ADD_ONLY, modify any unused colors at the end (matches
                the last color if more than one match)
        """
        # img = img.convert('P', palette=Image.ADAPTIVE, colors=16)
        img = img.convert('RGBA')
        if modify_tiles is not self.EDIT_ANY:
            if modify_screen is not self.EDIT_ANY:
                # Not yet implemented though
                raise ValueError('screen must be editable if tiles are not')
        pixels = img.load()
        # pal_str = img.palette.tostring()
        # clr.set_palette(0, img.getpalette())
        if modify_palette is self.EDIT_ANY:
            palettes = []
        else:
            palettes = clr.get_palettes()
        tiles = []
        changes_pal_ids = set()
        if modify_screen is self.EDIT_NONE:
            scr_x = scr_y = 0
            for tiledata in self.scrn.data:
                tile_id = tiledata & 0x3FF
                try:
                    tile = tiles[tile_id]
                except IndexError:
                    while tile_id+1 > len(tiles):
                        tile = []
                        for i in range(8):
                            tile.append([0]*8)
                        tiles.append(tile)
                if (tiledata >> 10) & 1:
                    flip_y_factor = -1
                else:
                    flip_y_factor = 1
                if (tiledata >> 11) & 1:
                    flip_x_factor = -1
                else:
                    flip_x_factor = 1
                pal_id = (tiledata >> 12) & 0xF
                try:
                    palette = palettes[pal_id]
                except:
                    while pal_id+1 > len(palettes):
                        palette = [(0xF8, 0xF8, 0xF8, 0)]
                        palettes.append(palette)
                for sub_y in range(8)[::flip_y_factor]:
                    for sub_x in range(8)[::flip_x_factor]:
                        pix = pixels[(scr_x+sub_x, scr_y+sub_y)]
                        if pix[3] < 0x80:
                            tile[sub_y][sub_x] = 0
                            continue
                        color = (pix[0] & 0xF8, pix[1] & 0xF8,
                                 pix[2] & 0xF8, 255)
                        try:
                            index = palette.index(color, 1)
                        except:
                            if modify_palette is self.EDIT_NONE:
                                raise ValueError('Some colors do not exist'
                                                 ' in current palette')
                            index = len(palette)
                            if index >= 16:
                                raise ValueError(
                                    'Cannot have more than 16 colors for'
                                    'image')
                            changes_pal_ids.add(pal_id)
                            palette.append(color)
                        tile[sub_y][sub_x] = index
                palettes[pal_id] = palette
                scr_x += 8
                if scr_x >= self.scrn.width:
                    scr_x = 0
                    scr_y += 8
                    if scr_y >= self.scrn.height:
                        break
        else:
            """minx, miny, maxx, maxy = img.getbbox()
            minx -= minx % 8
            miny -= miny % 8
            # Max do not need to be exact because of the loop condition
            maxx += 8
            maxy += 8"""
            if modify_tiles is self.ADD_ONLY:
                tiles = cgr.get_tiles()
            else:
                tiles = []
                tile = []
                for i in range(8):
                    tile.append([0]*8)
                tiles.append(tile)
            data = array.array('H')
            width, height = img.size
            for scr_y in range(0, height, 8):
                for scr_x in range(0, width, 8):
                    tiledata = 0
                    pal_id = 0  # Potentially allow this to be different
                    try:
                        palette = palettes[pal_id]
                    except:
                        while pal_id+1 > len(palettes):
                            palette = [(0xF8, 0xF8, 0xF8, 0)]
                            palettes.append(palette)
                    tile = []
                    for sub_y in range(8):
                        tile.append([0]*8)
                        for sub_x in range(8):
                            pix = pixels[(scr_x+sub_x, scr_y+sub_y)]
                            if pix[3] < 0x80:
                                tile[sub_y][sub_x] = 0
                                continue
                            color = (pix[0] & 0xF8, pix[1] & 0xF8,
                                     pix[2] & 0xF8, 255)
                            try:
                                index = palette.index(color, 1)
                            except:
                                if modify_palette is self.EDIT_NONE:
                                    raise ValueError('Some colors do not exist'
                                                     ' in current palette')
                                index = len(palette)
                                if index >= 16:
                                    raise ValueError(
                                        'Cannot have more than 16 colors for'
                                        'image')
                                changes_pal_ids.add(pal_id)
                                palette.append(color)
                            tile[sub_y][sub_x] = index
                    for tile_id, ref_tile in enumerate(tiles):
                        if ref_tile == tile:
                            break
                    else:
                        tiles.append(tile)
                        tile_id = len(tiles)-1
                    tiledata = tile_id | (pal_id << 12)
                    data.append(tiledata)
            self.scrn.width = scr_x+8
            self.scrn.height = scr_y+8
            self.scrn.data = data
        for pal_id in changes_pal_ids:
            clr.set_palette(pal_id, palettes[pal_id])
        if modify_tiles is not self.EDIT_NONE:
            cgr.set_tiles(tiles)
