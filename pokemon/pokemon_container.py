
from evo import Evolutions
from personal import Personal


class Pokemon(object):
    def __init__(self, game):
        self.game = game
        self.natid = None
        self.personal = Personal(version=game.game_name)
        self.evolutions = Evolutions()

    def load_id(self, natid):
        self.personal.load(self.game.get_personal(natid))
        self.evolutions.load(self.game.get_evo(natid))
        self.natid = natid

    @staticmethod
    def from_id(game, natid):
        target = Pokemon(game)
        target.load_id(natid)
        return target

    def save(self):
        if self.natid is None:
            raise ValueError('This Pokemon has no natid set')
        self.game.set_personal(self.natid, self.personal.save().getvalue())
        self.game.set_evo(self.natid, self.evolutions.save().getvalue())
