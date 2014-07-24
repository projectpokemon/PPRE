"""Texture Atoms"""

from rawdb.elements.atom import BaseAtom, ValenceFormatter


class SeekValence(ValenceFormatter):
    def __init__(self, field):
        super(SeekValence, self).__init__(None)
        self.field = field
        self.ignore = True

    def unpack_one(self, atomic):
        if hasattr(self.field, '__call__'):
            atomic.data.seek(self.field(atomic), 0)
        else:
            atomic.data.seek(atomic[self.field], 0)
        return None


class BTXAtom(BaseAtom):
    def __init__(self):
        super(BTXAtom, self).__init__()
        self.uint32('magic')
        self.uint32('size')
        self.texinfo('texinfo')
        self.texinfo('tex4x4info')
        self.uint32('tex4x4info_paletteofs')
        self.texinfo('palinfo', True)
        self.append_format(SeekValence(lambda atomic:
                                       atomic.texinfo.lookupofs))
        self.lookupdict('texdict')
        self.append_format(SeekValence(lambda atomic:
                                       atomic.palinfo.lookupofs))
        self.lookupdict('paldict')

        self.append_format(SeekValence(lambda atomic:
                                       atomic.texinfo.dataofs))
        self.data('texdata', lambda atomic: atomic.texinfo.datasize << 3)

        self.append_format(SeekValence(lambda atomic:
                                       atomic.tex4x4info.dataofs))
        self.data('tex4x4data', lambda atomic: atomic.tex4x4info.datasize << 3)

        self.append_format(SeekValence(lambda atomic:
                                       atomic.palinfo.dataofs))
        self.data('paldata', lambda atomic: atomic.palinfo.datasize << 3)

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
        self.sub_pop()

    def lookupdict(self, name):
        self.sub_push(name)
        self.uint8('version')
        self.uint8('num')
        self.uint16('size')
        self.uint16('dummy0')
        self.uint16('refofs')

        self.sub_push('nodes')
        self.uint8('ref')
        self.uint8('left')
        self.uint8('right')
        self.uint8('index')
        self.array(self.sub_pop(), count=0)

        self.append_format(SeekValence('refofs'))
        self.uint16('sizeunit')
        self.uint16('nameofs')
        self.array(self.uint8('data'), count=0)
        # self.append_format(SeekValence('nameofs'))
        self.array(self.string('names', 16), count=0)

        lookup = self.sub_pop()

        def format_iterator(atomic):
            for fmt in lookup.sub_formats:
                if fmt.name == 'nodes' or fmt.name == 'names':
                    fmt.count = atomic.num
                elif fmt.name == 'data':
                    fmt.count = atomic.num*atomic.sizeunit
                yield fmt
        lookup.format_iterator = format_iterator
