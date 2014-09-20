
from rawdb.elements.atom import BaseAtom


class G3DResDict(BaseAtom):
    def __init__(self):
        super(G3DResDict, self).__init__()
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
