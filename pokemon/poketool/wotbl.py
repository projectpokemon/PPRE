
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


from generic.editable import XEditable as Editable


class LevelMove(Editable):
    def __init__(self, version='Diamond'):
        self.version = version
        Editable.__init__(self)
        if version in game.GEN_IV:
            self.uint16('moveid', width=9, max_value=0x1FF)
            self.uint16('level', width=7, max_value=0x7F)
        else:
            self.uint16('moveid')
            self.uint16('level')
        self.freeze()

    def is_end(self):
        if self.version in game.GEN_IV:
            return self.moveid == 0x1FF
        return self.moveid == 0xFFFF

    @staticmethod
    def end(version='Diamond'):
        lvlmove = LevelMove(version)
        if version in game.GEN_IV:
            lvlmove.moveid = 0x1FF
            lvlmove.level = 0x7F
        else:
            lvlmove.moveid = 0xFFFF
            lvlmove.level = 0xFFFF
        return lvlmove


class LevelMoves(Editable):
    def __init__(self, version='Diamond', reader=None):
        self.version = version
        Editable.__init__(self)
        self.array('moves', LevelMove().base_struct, length=0)
        self.freeze()
        if reader is not None:
            self.load(reader)

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.moves = []
        while True:
            lvlmove = LevelMove(self.version)
            lvlmove.load(reader)
            if lvlmove.is_end():
                break
            else:
                self.moves.append(lvlmove)

    def save(self, writer=None):
        writer = writer if writer is not None else BinaryIO()
        for lvlmove in self.moves:
            writer = lvlmove.save(writer)
        writer = LevelMove.end(self.version).save(writer)
        return writer
