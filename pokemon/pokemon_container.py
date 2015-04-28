
from generic import Editable
from pokemon.poketool.evo import Evolutions
from pokemon.poketool.personal import Personal
from pokemon.poketool.wotbl import LevelMoves


class Pokemon(Editable):
    def define(self, game):
        self.game = game
        self.personal = Personal(game)
        self.restrict('personal')
        self.evolutions = Evolutions()
        self.restrict('evolutions')
        self.levelmoves = LevelMoves(game)
        self.restrict('levelmoves')
        self.name = ''
        self.restrict('name')
        self.names = game.text(game.locale_text_id('pokemon_names'))
        self.species_name = ''
        self.restrict('species_name')
        self.species_names = game.text(game.locale_text_id('species_names'))

    def load_id(self, natid):
        self.personal.load(self.game.get_personal(natid))
        self.evolutions.load(self.game.get_evo(natid))
        self.levelmoves.load(self.game.get_wotbl(natid))
        self.name = self.names[natid]
        self.species_name = self.species_names[natid]
        return self

    @classmethod
    def from_id(cls, game, natid):
        target = cls(game)
        target.load_id(natid)
        return target

    def commit(self, natid):
        self.game.set_personal(natid, self.personal)
        self.game.set_evo(natid, self.evolutions)
        self.game.set_wotbl(natid, self.levelmoves)
        if self.name != self.names[natid]:
            self.names[natid] = self.name
            self.game.set_text(self.game.locale_text_id('pokemon_names'),
                               self.names)
        if self.species_name != self.species_names[natid]:
            self.species_names[natid] = self.species_name
            self.game.set_text(self.game.locale_text_id('species_names'),
                               self.species_names)
