
from util import BinaryIO


class LevelMove(object):
    def __init__(self, moveid, level):
        self.moveid = moveid
        self.level = level

    @property
    def move(self):
        raise NotImplementedError('Cannot build move')


class LevelMoves(object):
    def __init__(self, reader=None):
        self.moves = []
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.moves = []
        while True:
            moveid = reader.readUInt16()
            if moveid == 0xFFFF:
                break
            level = (moveid >> 9) & 0x7F
            moveid = moveid & 0x1FF
            self.moves.append(LevelMove(moveid, level))

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        for lvlmove in self.moves:
            writer.writeUInt16(lvlmove.moveid | (lvlmove.level << 9))
        writer.writeUInt16(0xFFFF)
        return writer
