
from collections import namedtuple

from rawdb.util.io import BinaryIO


Node = namedtuple('Node', 'ref left right index')


class G3DResDict(object):
    def __init__(self):
        self.nodes = []
        self.data = ''
        self.names = []

    def load(self, reader):
        start = reader.tell()
        self.version = reader.readUInt8()
        num = reader.readUInt8()
        size = reader.readUInt16()
        refofs = reader.readUInt16()
        self.nodes = []
        for i in xrange(num):
            self.nodes.append(Node(reader.readUInt8(), reader.readUInt8(),
                                   reader.readUInt8(), reader.readUInt8()))
        reader.seek(start+refofs)
        sizeunit = reader.readUInt16()
        nameofs = reader.readUInt16()
        self.data = reader.read(sizeunit*num)
        for i in xrange(num):
            self.names.append(reader.read(16))
