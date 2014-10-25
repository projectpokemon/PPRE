
from util import BinaryIO


class Evolution(object):
    def __init__(self, method, parameter, target):
        self.method = method
        self.parameter = parameter
        self.target = target


class Evolutions(object):
    def __init__(self, reader=None):
        self.evos = []
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.evos = []
        for i in xrange(7):
            evo = Evolution(reader.readUInt16(), reader.readUInt16(),
                            reader.readUInt16())
            if evo.method or evo.target:
                self.evos.append(evo)

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        start = writer.tell()
        for evo in self.evos:
            writer.writeUInt16(evo.method)
            writer.writeUInt16(evo.param)
            writer.writeUInt16(evo.target)
        writer.writePadding(start+44)
        return writer
