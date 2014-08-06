"""Texture Atoms"""

import struct

from PIL import Image

from rawdb.elements.atom import BaseAtom, AtomicInstance

COLOR0 = '\x00\x00\x00\x00'


class BTXAtomicInstance(AtomicInstance):
    @property
    def images(self):
        images = []
        for param in self.texparams:
            data = ''
            pal = [chr(i)*4 for i in xrange(256)]
            if param['format'] == 1:  # A3I5
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    value = ord(value)
                    index = value & 0x1F
                    alpha = ((value >> 5) & 0x7)*36
                    if index or param['color0']:
                        data += pal[index][:3]+chr(alpha)
                    else:
                        data += COLOR0
                img = Image.frombytes('RGBA',
                                      (param['width'], param['height']), data)
                images.append(img)
            elif param['format'] == 2:  # I2 4 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     (param['width']*param['height'] >> 2)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 2):
                        index = value >> shift & 0x3
                        if index or param['color0']:
                            data += pal[index]
                        else:
                            data += COLOR0
                img = Image.frombytes('RGBA',
                                      (param['width'], param['height']), data)
                images.append(img)
            elif param['format'] == 3:  # I4 16 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     (param['width']*param['height'] >> 1)]
                for value in block:
                    value = ord(value)
                    for shift in xrange(0, 8, 4):
                        index = value >> shift & 0xF
                        if index or param['color0']:
                            data += pal[index]
                        else:
                            data += COLOR0
                img = Image.frombytes('RGBA',
                                      (param['width'], param['height']), data)
                images.append(img)
            elif param['format'] == 4:  # I8 256 colors
                block = self.texdata[param['ofs']:param['ofs'] +
                                     param['width']*param['height']]
                for value in block:
                    index = ord(value)
                    if index or param['color0']:
                        data += pal[index]
                    else:
                        data += COLOR0
                img = Image.frombytes('RGBA',
                                      (param['width'], param['height']), data)
                images.append(img)
            continue
            for i in xrange(param['width']*param['height']):
                value = ord(self.texdata[param['ofs']+i])
                if param['format'] == 1:  # A3I5
                    index = value & 0x1F
                    alpha = ((value >> 5) & 0x7)*36
                    data.append(pal[index][:3]+[alpha])
                elif param['format'] == 3:  # 16 colors
                    index = value & 0xF
                    if index or param['color0']:
                        data.append(pal[index])
                    else:
                        data.append([255, 255, 255, 0])
                    index = (value >> 4) & 0xF
                    if index or param['color0']:
                        data.append(pal[index])
                    else:
                        data.append([255, 255, 255, 0])
                else:
                    continue
                    raise RuntimeError('No such format: %d' % param['format'])
        for i, img in enumerate(images):
            img.save('%d.png' % i)
        return images

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
