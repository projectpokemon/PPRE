

class GameAdapter(object):
    def __init__(self, game):
        self.game = game

    def load_archive(self, filename):
        return self.game.archive(filename)


class BaseElement(GameAdapter):
    pass
