

class GameAdapter(object):
    def __init__(self, game):
        self.observed = {}
        self.game = game

    def load_archive(self, filename):
        """ Load archive from local filename """
        self.archive = self.game.archive(filename)

    def save(self):
        """ Save changes to archive """
        # TODO: Pass observed dict to archive.
        if self.observed:
            self.archive.write()


class BaseElement(GameAdapter):
    def __len__(self):
        return len(self.archive)

    def __getitem__(self, key):
        self.observed[key] = True
        return self.atom(self.archive[key])

    def __iter__(self):
        for x in xrange(len(self)):
            yield x

    def __contains__(self, item):
        return item in self.keys()

    def keys(self):
        return list(self.__iter__())
