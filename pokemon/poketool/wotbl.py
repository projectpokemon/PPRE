
from generic import Editable
from util import BinaryIO


class LevelMove(Editable):
    def define(self, game):
        self.game = game
        if game.gen == 4:
            self.uint16('moveid', width=9)
            self.uint16('level', width=7)
        else:
            self.uint16('moveid')
            self.uint16('level')

    def is_end(self):
        if self.game.gen == 4:
            return self.moveid == 0x1FF
        return self.moveid == 0xFFFF

    @staticmethod
    def end(game):
        lvlmove = LevelMove(game)
        if game.gen == 4:
            lvlmove.moveid = 0x1FF
            lvlmove.level = 0x7F
        else:
            lvlmove.moveid = 0xFFFF
            lvlmove.level = 0xFFFF
        return lvlmove


class LevelMoves(Editable):
    def define(self, game):
        self.game = game
        self.moves = []
        self.restrict('moves')

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        self.moves = []
        while True:
            lvlmove = LevelMove(self.game, reader=reader)
            if lvlmove.is_end():
                break
            else:
                self.moves.append(lvlmove)

    def save(self, writer=None):
        writer = BinaryIO.writer(writer)
        for lvlmove in self.moves:
            writer = lvlmove.save(writer)
        writer = LevelMove.end(self.game).save(writer)
        return writer
