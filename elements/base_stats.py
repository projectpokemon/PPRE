
from rawdb.elements import BaseElement


class BaseStats(BaseElement):
    def __init__(self, game):
        super(BaseStats, self).__init__(game)
        self.load_archive(self.game.base_stat_file)
        self.atom = self.game.base_stat_atom()

