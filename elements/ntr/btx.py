"""Texture Atoms"""

import struct

from PIL import Image

from rawdb.elements.atom import BaseAtom, AtomicInstance

COLOR0 = '\x00\x00\x00\x00'


class BTXAtomicInstance(AtomicInstance):
    @property
    def bitmaps(self):
        """List of 2d bitmaps

        Each pixel is a tuple of (index, alpha)
        """
        bitmaps = []
        for param in self.texparams:
            pixels = []  # 1d
            if param['format'] == 1:  # A3I5
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    value = ord(value)
                    index = value & 0x1F
                    alpha = ((value >> 5) & 0x7)*36
                    if not index and not param['color0']:
                        alpha = 0
                    pixels += [(index, alpha)]
            elif param['format'] == 2:  # I2 4 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     (param['width']*param['height'] >> 2)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 2):
                        index = value >> shift & 0x3
                        alpha = None
                        if not index and not param['color0']:
                            alpha = 0
                        pixels += [(index, alpha)]
            elif param['format'] == 3:  # I4 16 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     (param['width']*param['height'] >> 1)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 4):
                        index = value >> shift & 0xF
                        alpha = None
                        if not index and not param['color0']:
                            alpha = 0
                        pixels += [(index, alpha)]
            elif param['format'] == 4:  # I8 256 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    index = ord(value)
                    alpha = None
                    if not index and not param['color0']:
                        alpha = 0
                    pixels += [(index, alpha)]
            elif param['format'] == 6:  # A5I3
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    value = ord(value)
                    index = value & 0x7
                    alpha = ((value >> 3) & 0x1F)*8
                    if not index and not param['color0']:
                        alpha = 0
                    pixels += [(index, alpha)]
            pixels2d = [pixels[i:i+param['width']]
                        for i in xrange(0, len(pixels), param['width'])]
            # img = Image.frombytes('RGBA', (param['width'], param['height']),
            #                       data)
            bitmaps.append(pixels2d)
        return bitmaps

    @property
    def texparams(self):
        # 8 bytes per param
        params = []
        for i in xrange(self.texdict.num):
            imgParam, extra = struct.unpack('II',
                                            self.texdict.data_[i*8:i*8+8])
            params.append({
                'ofs': (imgParam & 0xFFFF) << 3,
                'width': 8 << ((imgParam >> 20) & 0x7),
                'height': 8 << ((imgParam >> 23) & 0x7),
                'format': (imgParam >> 26) & 0x7,
                'color0': (imgParam >> 29) & 0x1
            })
        return params

    @property
    def palparams(self):
        # 4 bytes per param
        params = []
        for i in xrange(self.paldict.num):
            offset, flag = struct.unpack('HH', self.paldict.data_[i*4:i*4+4])
            params.append({
                'ofs': offset << 3,
                'count4': flag
            })
        return params

    @property
    def palettes(self):
        data = self.paldata
        palettes = []
        for param in self.palparams:
            palette = []
            values = [ord(b) for b in self.paldata[param['ofs']:
                                                   param['ofs']+512]]
            for value in values:
                palette.append(struct.pack('4B',
                                           (value >> 0 & 0x1F) << 3,
                                           (value >> 5 & 0x1F) << 3,
                                           (value >> 10 & 0x1F) << 3,
                                           255))
            palettes.append(palette)
        return palettes

    @property
    def imagemap(self):
        """List of (bitmap, palette) pairs
        """
        try:
            return self._imagemap
        except:
            imagemap = []
            if self.paldict.num == self.texdict.num:
                imagemap = zip(xrange(self.texdict.num),
                               xrange(self.paldict.num))
            else:  # Mtx Merger
                for texidx, texname in enumerate(self.texdict.names):
                    match = 0
                    best = 0
                    for palidx, palname in enumerate(self.paldict.names):
                        for c in xrange(16):
                            try:
                                if palname[c] != texname[c]:
                                    break
                            except:
                                break
                        if c > match:
                            match = c
                            best = palidx
                    imagemap.append((texidx, best))
            super(AtomicInstance, self).__setattr__('_imagemap', imagemap)
            return imagemap

    @imagemap.setter
    def imagemap(self, value):
        super(AtomicInstance, self).__setattr__('_imagemap', value)

    @property
    def images(self):
        """List of PIL Images as built from self.imagemap
        """
        palettes = self.palettes
        bitmaps = self.bitmaps
        images = []
        for palidx, texidx in self.imagemap:
            palette = palettes[palidx]
            bitmap = bitmaps[texidx]
            data = ''
            for row in bitmap:
                for pix in row:
                    if pix[1] is None:
                        data += palette[pix[0]]
                    else:
                        data += palette[pix[0]][:3] + chr(pix[1])
            images.append(Image.frombytes('RGBA', (len(row), len(bitmap)),
                                          data))
        return images


class BTXAtom(BaseAtom):
    atomic = BTXAtomicInstance

    def __init__(self):
        super(BTXAtom, self).__init__()
        start = self.uint32('magic')
        self.uint32('size')
        texinfo = self.texinfo('texinfo')
        tex4x4info = self.texinfo('tex4x4info')
        self.uint32('tex4x4info_paletteofs')
        palinfo = self.texinfo('palinfo', True)

        self.seek(texinfo.lookupofs, start=start)
        self.lookupdict('texdict')

        self.seek(palinfo.lookupofs, start=start)
        self.lookupdict('paldict')

        self.seek(texinfo.dataofs, start=start)
        self.data('texdata', texinfo.datasize << 3)

        self.seek(tex4x4info.dataofs, start=start)
        self.data('tex4x4data', tex4x4info.datasize << 2)

        self.seek(palinfo.dataofs, start=start)
        self.data('paldata', palinfo.datasize << 3)

    def texinfo(self, name, late_lookup=False):
        """
        Parameters
        ----------
        name : string
            Suffix for fields
        late_lookup : bool
            If true, {name}_lookupofs will just before the dataofs
        """
        self.sub_push(name)
        self.uint32('vramkey')
        self.uint16('datasize')  # data_size <<= 3
        if not late_lookup:
            self.uint16('lookupofs')
        self.uint16('loaded')  # Runtime-only
        # self.padding(2)
        if late_lookup:
            self.uint16('lookupofs')
        self.uint16('dummy0')
        self.uint32('dataofs')
        return self.sub_pop()

    def lookupdict(self, name):
        self.sub_push(name)
        start = self.uint8('version')
        num = self.uint8('num')
        self.uint16('size')
        self.uint16('dummy0')
        refofs = self.uint16('refofs')

        self.sub_push('nodes')
        self.uint8('ref')
        self.uint8('left')
        self.uint8('right')
        self.uint8('index')
        self.array(self.sub_pop(), count=num)

        self.seek(refofs, start=start)
        sizeunit = self.uint16('sizeunit')
        nameofs = self.uint16('nameofs')
        self.data('data_', num*sizeunit)
        self.seek(nameofs, start=sizeunit)
        self.array(self.string('names', 16), count=num)

        return self.sub_pop()
