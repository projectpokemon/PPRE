
from util import BinaryIO


class HeaderBin(object):
    """Handler for header.bin

    Attributes
    ----------
    name : string
        Name for this game. Up to 12 chars
    code : string
        Code for this game. Up to 4 chars
    base_code : string
        Base ROM code. 4 chars. Read-only
    """
    def __init__(self, reader=None):
        self.name = ''
        self.code = ''
        self.base_code = ''
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        self.name = reader.read(12).rstrip('\x00')
        self.code = reader.read(4)
        with reader.seek(start+0xA0):
            self.base_code = reader.read(4).rstrip('\x00')
        if not self.base_code:
            self.base_code = self.code

    def save(self):
        """Save necessary information. NDSTool cleans up the rest"""
        writer = BinaryIO('\x00'*0x200)
        writer.write(self.name)
        with writer.seek(0xC):
            writer.write(self.code)
        with writer.seek(0x10):
            writer.write('01')  # Nintendo
        with writer.seek(0x60):
            writer.writeUInt32(0x7f7fff)
            writer.writeUInt32(0x7f1fff)
            writer.writeUInt32(0)
            writer.writeUInt32(0)
            writer.writeUInt32(0x051E)
        with writer.seek(0xA0):
            writer.write(self.base_code)
        writer.seek(0x200)
        return writer
