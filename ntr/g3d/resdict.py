
from collections import namedtuple

from rawdb.util.io import BinaryIO


Node = namedtuple('Node', 'ref left right index')


class G3DResDict(object):
    def __init__(self):
        self.nodes = []
        self.data = []
        self.names = []
        self.sizeunit = 4
        self.version = 2

    @property
    def num(self):
        return len(self.data)

    @num.setter
    def num(self, value):
        old = self.num
        if value < old:
            self.data = self.data[:value]
        else:
            self.data.extend(['']*(value-old))

    def load(self, reader):
        start = reader.tell()
        self.version = reader.readUInt8()
        num = reader.readUInt8()
        size = reader.readUInt16()
        reader.readUInt16()
        refofs = reader.readUInt16()
        self.nodes = []
        for i in xrange(num):
            self.nodes.append(Node(reader.readUInt8(), reader.readUInt8(),
                                   reader.readUInt8(), reader.readUInt8()))
        reader.seek(start+refofs)
        self.sizeunit = reader.readUInt16()
        nameofs = reader.readUInt16()
        for i in xrange(num):
            self.data.append(reader.read(self.sizeunit))
        for i in xrange(num):
            self.names.append(reader.read(16))

    def save(self, writer=None):
        if writer is None:
            writer = BinaryIO()
        start = writer.tell()
        writer.writeUInt8(self.version)
        num = len(self.data)
        writer.writeUInt8(num)
        sizeofs = writer.tell()
        writer.writeUInt16(0)
        writer.writeUInt16(8)
        writer.writeUInt16(0)  # refofs
        for i in xrange(num):
            # TODO: Build PTree. Although it isn't actually used
            try:
                node = self.nodes[i]
            except:
                node = Node(0, 0, 0, 0)
            for j in xrange(4):
                writer.writeUInt8(node[j])
        writer.writeAlign(4)
        namerel = writer.tell()
        refofs = namerel-start
        writer.writeUInt16(self.sizeunit)
        nameofsofs = writer.tell()
        writer.writeUInt16(0)
        for i in xrange(num):
            writer.write(self.data[i])
            if len(self.data[i]) < self.sizeunit:
                writer.write('\x00'*(self.sizeunit-len(self.data[i])))
        nameofs = writer.tell()-namerel
        with writer.seek(nameofsofs):
            writer.writeUInt16(nameofs)
        nameofs = writer.tell()
        for i in xrange(num):
            writer.write(self.names[i])
            writer.writePadding(nameofs+i*16)
        size = writer.tell()-start
        with writer.seek(sizeofs):
            writer.writeUInt16(size)
            writer.writeUInt16(8)
            writer.writeUInt16(refofs)
        return writer
