
from generic import Editable


class Ability(Editable):
    def define(self, game):
        self.game = game
        self.name = ''
        self.flavor = ''
        self.restrict('name')
        self.restrict('flavor')
        self.names = game.text(game.locale_text_id('ability_names'))
        self.flavors = game.text(
            game.locale_text_id('ability_flavors'))

    def load_id(self, ability_id):
        self.name = self.names[ability_id]
        self.flavor = self.flavors[ability_id]

    def commit(self, ability_id):
        if self.name != self.names[ability_id]:
            self.names[ability_id] = self.name
            self.game.set_text(self.game.locale_text_id('ability_names'),
                               self.names)
        if self.flavor != self.flavors[ability_id]:
            self.flavors[ability_id] = self.flavor
            self.game.set_text(
                self.game.locale_text_id('ability_flavors'),
                self.flavors)
