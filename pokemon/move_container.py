
from generic.editable import Editable
from pokemon.poketool.waza import Waza


class Move(Editable):
    def __init__(self, game):
        self.game = game
        self.moveid = None
        self.restrict('moveid', min_value=0)
        self.waza = Waza(version=game.game_name)
        self.restrict('waza')

    def load_id(self, moveid):
        self.waza.load(self.game.get_waza(moveid))
        self.moveid = moveid

    @staticmethod
    def from_id(game, moveid):
        target = Move(game)
        target.load_id(moveid)
        return target

    def save(self):
        if self.moveid is None:
            raise ValueError('This Move has no moveid set')
        self.game.set_waza(self.moveid, self.waza.save().getvalue())
