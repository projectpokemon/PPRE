
import array
import itertools

from PIL import Image

from generic.editable import XEditable as Editable


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


class NSCR(Editable):
    EDIT_NONE = 0
    EDIT_ANY = 1
    ADD_ONLY = 2

    def define(self):
        self.string('magic', length=4, default='RSCN')
        self.uint16('endian', default=0xFFFE)
        self.uint16('version', default=0x100)
        self.uint32('size')
        self.uint16('headersize', default=0x10)
        self.uint16('numblocks', default=1)
        self.scrn = SCRN(self)

    def load(self, reader):
        Editable.load(self, reader)
        self.scrn.load(reader)

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
            for pal_id in changes_pal_ids:
                clr.set_palette(pal_id, palettes[pal_id])
            cgr.set_tiles(tiles)
        else:
            raise NotImplementedError('Cannot yet modify screen')
