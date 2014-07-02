

class GameAdapter(object):
    def __init__(self, game):
        self.game = game

    def load_archive(self, filename):
        self.archive = self.game.archive(filename)


class BaseElement(GameAdapter):
    def __len__(self):
        return len(self.archive)

    def __getitem__(self, key):
        return self.atom(self.archive[key])

    def __iter__(self):
        for x in xrange(len(self)):
            yield x

    def __contains__(self, item):
        return item in self.keys()

    def keys(self):
        return list(self.__iter__())
