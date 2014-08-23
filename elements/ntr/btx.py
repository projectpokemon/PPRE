"""Texture Atoms"""

from cStringIO import StringIO
import struct
import zipfile

from PIL import Image

from rawdb.elements.atom import BaseAtom, AtomicInstance
from rawdb.elements.atom.atomic import ThinAtomicInstance

COLOR0 = '\x00\x00\x00\x00'


def log2(x):
    """Integer log2"""
    return x.bit_length()-1


class BTXAtomicInstance(AtomicInstance):
    PALETTE_BRUTE_FORCE = 1  # Unoptimized horrible palette blob... that works

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
                    if not index and param['color0']:
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
                        if not index and param['color0']:
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
                        if not index and param['color0']:
                            alpha = 0
                        pixels += [(index, alpha)]
            elif param['format'] == 4:  # I8 256 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    index = ord(value)
                    alpha = None
                    if not index and param['color0']:
                        alpha = 0
                    pixels += [(index, alpha)]
            elif param['format'] == 6:  # A5I3
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    value = ord(value)
                    index = value & 0x7
                    alpha = ((value >> 3) & 0x1F)*8
                    if not index and param['color0']:
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
            data = self.paldata[param['ofs']:param['ofs']+512]
            values = [struct.unpack('H', data[i:i+2])[0]
                      for i in xrange(0, len(data), 2)]
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
        try:
            return self._images
        except:
            pass
        palettes = self.palettes
        bitmaps = self.bitmaps
        images = []
        for texidx, palidx in self.imagemap:
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
        super(AtomicInstance, self).__setattr__('_images', images)
        return images

    @images.setter
    def images(self, value):
        super(AtomicInstance, self).__setattr__('_images', value)

    def export(self, handle):
        """An archive with all files"""
        with zipfile.ZipFile(handle, 'w') as archive:
            for idx, image in enumerate(self.images):
                buffer = StringIO()
                image.save(buffer, format='PNG')
                archive.writestr('%03d.png' % idx, buffer.getvalue())
                buffer.close()
        return handle

    def load(self, handle):
        """Build images from an archive"""
        with zipfile.ZipFile(handle, 'r') as archive:
            images = []
            for name in archive.namelist():
                # TODO: sanitize sizes, etc.
                img = Image.open(StringIO(archive.read(name)))
                images.append(img.convert('RGBA'))
        self.images = images
        self.build_from_images()

    def build_from_images(self):
        """Take the modified image dictionary and commit changes to
        the other data structures
        """
        processed = 0
        images = self.images
        imagemap = zip(xrange(len(images)), [0]*len(images))
        pal0 = ['\x00\x00']*256
        pal1idx = 1  # max 32
        pal4idx = 255  # min pal1idx
        self.texdata = ''  # Delete old images
        self.texdict.data_ = ''
        for texidx, palidx in imagemap:
            tex = []
            format = 4
            for pix in images[texidx].getdata():
                alpha = pix[3]
                if not alpha:  # color0=1
                    tex.append(0)
                    continue
                color = (pix[0] >> 3) << 0 |\
                    (pix[1] >> 3) << 5 |\
                    (pix[2] >> 3) << 10
                color = struct.pack('H', color)
                if alpha < 216:  # 216 = 6*36 (max non-solid value for A3I5)
                    try:
                        index = pal0[:32].index(color, 1)
                    except ValueError:
                        pal0[pal1idx] = color
                        index = pal1idx
                        pal1idx += 1
                        if pal1idx > 32:
                            raise OverflowError('Too many colors with alphas.'
                                                ' Max 32 for all images.')
                    format = 1
                else:
                    try:
                        index = pal0.index(color, 1)
                    except ValueError:
                        pal0[pal4idx] = color
                        index = pal4idx
                        pal4idx -= 1
                if pal4idx < pal1idx:
                    raise OverflowError('Cannot have more than 256 colors'
                                        ' for all images')
                tex.append(index)
            ofs = len(self.texdata) >> 3
            size = images[texidx].size
            self.texdict.data_ += struct.pack('II', ofs |
                                              (log2(size[0] >> 3) << 20) |
                                              (log2(size[1] >> 3) << 23) |
                                              (format << 26) | (1 << 29), 0)
            self.texdata += ''.join([chr(c) for c in tex])
            ofs = len(self.texdata)
            self.texdata += '\x00'*(8 - (ofs % 8))  # Align
        self.paldata = ''.join(pal0)
        self.imagemap = imagemap
        self.texdict.num = len(images)
        self.paldict.num = len(images)
        self.paldict.data_ = '\x00\x00\x00\x00'*self.paldict.num
        self.paldict.names = ['palette_all_%03d\x00' % i for i in xrange(self.paldict.num)]
        self.texdict.names = ['image_%03d\x00\x00\x00\x00\x00\x00\x00' % i
                              for i in xrange(self.texdict.num)]
        self.texdict.nodes = [ThinAtomicInstance('\x00\x00\x00\x00')] * \
            self.texdict.num
        self.paldict.nodes = [ThinAtomicInstance('\x00\x00\x00\x00')] * \
            self.paldict.num
        self.texdict.sizeunit = 8
        self.paldict.sizeunit = 4
        self.texdict.version = 0xFF
        self.paldict.version = 0xFF
        # HACK: Correction for datasize not being updated on save
        self.texinfo.datasize = len(self.texdata) >> 3
        self.palinfo.datasize = len(self.paldata) >> 3

    def __str__(self):
        # self.build_from_images()
        return super(BTXAtomicInstance, self).__str__()


class BTXAtom(BaseAtom):
    atomic = BTXAtomicInstance

    def __init__(self):
        super(BTXAtom, self).__init__()
        start = self.uint32('magic')
        size = self.uint32('size')
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
        self.seek(size, start=start)

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
        dictsize = self.uint16('size')
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
        self.seek(dictsize, start=start)

        return self.sub_pop()
