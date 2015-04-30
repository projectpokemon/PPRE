
from util import BinaryIO


class FileSystem(object):
    """Provides lookups for files by their id

    This is not an alternative to NDSTool. This is Pokemon/SDK specific.
    """
    def __init__(self, game):
        self.game = game
        self.filenames = []
        self.load()

    def load(self):
        self.filenames = []
        with self.game.open('arm9.dec.bin') as arm9:
            reader = BinaryIO.reader(arm9)
            reader.seek(self.game.file_system_table[1])
            while True:
                offset = reader.readUInt32()
                if not offset:
                    break
                with reader.seek(offset-0x02000000):  # TODO: BW ram ofs
                    self.filenames.append(reader.readString())

    def save(self):
        raise NotImplementedError('Cannot save changed filesystem')
