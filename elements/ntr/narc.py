
from rawdb.elements.atom import BaseAtom, AtomicInstance


class NARCAtomicInstance(AtomicInstance):
    pass


class NARCAtom(BaseAtom):
    atomic = NARCAtomicInstance

    def __init__(self):
        super(NARCAtom, self).__init__()

        start = self.uint32('magic')
        self.int16('endian')
        self.uint16('version')
        size = self.uint32('size')
        headersize = self.uint16('headersize')
        self.uint16('numblocks')

        self.seek(headersize, start=start)
        self.sub_atom('fatb', FATBAtom())
        self.sub_atom('fntb', FNTBAtom())
        self.sub_atom('fimg', FIMGAtom())
        self.seek(size, start=start)


class FATBAtom(BaseAtom):

    def __init__(self):
        super(FATBAtom, self).__init__()

        start = self.uint32('magic')
        size = self.uint32('size')
        num = self.uint16('num')
        self.uint16('reserved')

        self.sub_push('entries')
        self.uint32('start')
        self.uint32('end')
        self.array(self.sub_pop(), count=num)
        self.seek(size, start=start)


class FNTBAtom(BaseAtom):

    def __init__(self):
        super(FNTBAtom, self).__init__()


class FIMGAtom(BaseAtom):

    def __init__(self):
        super(FIMGAtom, self).__init__()

