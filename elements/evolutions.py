
from rawdb.elements import BaseElement


class Evolutions(BaseElement):
    def __init__(self, game):
        super(Evolutions, self).__init__(game)
        self.load_archive(self.game.evolutions_file)
        self.atom = self.game.evolutions_atom()

