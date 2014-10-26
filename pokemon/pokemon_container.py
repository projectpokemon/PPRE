
from generic.editable import Editable
from pokemon.poketool.evo import Evolutions
from pokemon.poketool.personal import Personal
from pokemon.poketool.wotbl import LevelMoves


class Pokemon(Editable):
    def __init__(self, game):
        self.game = game
        self.natid = None
        self.restrict('natid', min_value=0)
        self.personal = Personal(version=game.game_name)
        self.restrict('personal')
        self.evolutions = Evolutions()
        self.restrict('evolutions')
        self.levelmoves = LevelMoves()
        self.restrict('levelmoves')

    def load_id(self, natid):
        self.personal.load(self.game.get_personal(natid))
        self.evolutions.load(self.game.get_evo(natid))
        self.levelmoves.load(self.game.get_wotbl(natid))
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
        self.game.set_wotbl(self.natid, self.evolutions.save().getvalue())
