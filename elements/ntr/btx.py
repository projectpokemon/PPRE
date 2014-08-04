"""Texture Atoms"""

import struct

from rawdb.elements.atom import BaseAtom, AtomicInstance


class BTXAtomicInstance(AtomicInstance):
    @property
    def images(self):
        images = []
        for param in self.texparams:
            images.append(0)
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
                'width': (imgParam >> 20) & 0x7,
                'height': (imgParam >> 23) & 0x7,
                'format': (imgParam >> 26) & 0x7,
                'enable': (imgParam >> 29) & 0x1
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
