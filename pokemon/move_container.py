
from generic import Editable
from pokemon.poketool.waza import Waza


class Move(Editable):
    def define(self, game):
        self.game = game
        self.waza = Waza(game)
        self.restrict('waza')
        self.name = ''
        self.names = game.text(game.locale_text_id('move_names'))
        self.using_moves = game.text(game.locale_text_id('using_moves'))
        self.restrict('name')

    def load_id(self, move_id):
        self.waza.load(self.game.get_waza(move_id))
        self.name = self.names[move_id]
        return self

    @classmethod
    def from_id(cls, game, move_id):
        target = cls(game)
        target.load_id(move_id)
        return target

    def commit(self, move_id):
        self.game.set_waza(move_id, self.waza)
        if self.name != self.names[move_id]:
            self.names[move_id] = self.name
            self.game.set_text(self.game.locale_text_id('move_names'),
                               self.names)
            # TODO: custom usage strings
            self.using_moves[move_id*3] = 'VAR(257, 0, 0) used\n{0}!'.format(self.name)
            self.using_moves[move_id*3+1] = 'The wild VAR(257, 0, 0) used\n{0}!'.format(self.name)
            self.using_moves[move_id*3+2] = 'The foe\'s VAR(257, 0, 0) used\n{0}!'.format(self.name)
            self.game.set_text(self.game.locale_text_id('using_moves'),
                               self.using_moves)
