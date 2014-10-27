
from generic.editable import Editable
import pokemon.game as game
from util import BinaryIO


class LevelMove(Editable):
    def __init__(self, moveid, level, version='Diamond'):
        # TODO: Varying restrictions per game
        self.moveid = moveid
        self.level = level
        if version in game.GEN_V:
            self.restrictUInt16('moveid')
            self.restrictUInt16('level')
        else:
            self.restrictUInt16('moveid', max_value=0x1FF)
            self.restrictUInt16('level', max_value=0x7F)

    @property
    def move(self):
        raise NotImplementedError('Cannot build move')


class LevelMoves(Editable):
    def __init__(self, reader=None, version='Diamond'):
        self.version = version
        self.moves = []
        self.restrict('moves', max_length=20)
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.moves = []
        while True:
            moveid = reader.readUInt16()
            if moveid == 0xFFFF:
                break
            if self.version in game.GEN_V:
                level = reader.readUInt16()
            else:
                level = (moveid >> 9) & 0x7F
                moveid = moveid & 0x1FF
            self.moves.append(LevelMove(moveid, level, self.version))

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        for lvlmove in self.moves:
            if self.version in game.GEN_V:
                writer.writeUInt16(lvlmove.moveid)
                writer.writeUInt16(lvlmove.level)
            else:
                writer.writeUInt16(lvlmove.moveid | (lvlmove.level << 9))
        writer.writeUInt16(0xFFFF)
        return writer
