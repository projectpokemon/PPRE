
from rawdb.elements.atom import BaseAtom, AtomicInstance, DictAtomicInstance


class NARCAtomicInstance(AtomicInstance):
    @property
    def files(self):
        return self.fimg.files

    @property
    def fimg(self):
        fimg = self.__getattr__('fimg')
        fimg.fatb = self.fatb
        return fimg

    def __str__(self):
        self.fimg.update()
        return super(NARCAtomicInstance, self).__str__()


class FIMGAtomicInstance(AtomicInstance):
    @property
    def fatb(self):
        return self.local_attr('fatb')

    @fatb.setter
    def fatb(self, value):
        return self.local_attr('fatb', value)

    @property
    def files(self):
        return [self.data_[entry.start:entry.end]
                for entry in self.fatb.entries]

    def update(self):
        offset = 0
        entries = []
        entry = self.fatb._packer.find_format('entries').sub_valence
        for data in self.files:
            size = len(data)
            self.data_ += data
            entries.append(DictAtomicInstance(
                self.fatb._packer.find_format('entries').sub_valence,
                {'start': offset, 'end': offset+size}))
            offset += size
        self.fatb.entries = entries


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

        start = self.uint32('magic')
        size = self.uint32('size')
        self.data('data_', size-8)
        self.seek(size, start=start)


class FIMGAtom(BaseAtom):
    atomic = FIMGAtomicInstance

    def __init__(self):
        super(FIMGAtom, self).__init__()

        start = self.uint32('magic')
        size = self.uint32('size')
        self.data('data_', count=size-8)
        self.seek(size, start=start)

