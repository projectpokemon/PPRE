
from rawdb.elements import BaseElement


class LevelMoves(BaseElement):
    def __init__(self, game):
        super(LevelMoves, self).__init__(game)
        self.load_archive(self.game.level_moves_file)
        self.atom = self.game.level_moves_atom()

