
from util import BinaryIO


class HeaderBin(object):
    """Handler for ncch_header.bin

    Attributes
    ----------
    code : string
        Code for this game. Up to 4 chars
    base_code : string
        Base ROM code. 4 chars. Read-only
    """
    def __init__(self, reader=None):
        self.code = ''
        self.base_code = ''
        self.data = ''
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        self.data = reader.read(512)  # Entire contents
        with reader.seek(start+0x156):
            self.code = self.base_code = reader.read(4)

    def save(self):
        """Save existing blob"""
        return BinaryIO(self.data)
