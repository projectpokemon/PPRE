
from generic import Editable


class Stats(Editable):
    STATS = ['hp', 'attack', 'defense', 'speed', 'spatk', 'spdef']

    def define(self, full=True):
        for stat in self.STATS:
            if full:
                self.uint8(stat)
            else:
                self.uint8(stat, width=2)


class Personal(Editable):
    def define(self, game):
        self.game = game
        self.struct('base_stat', Stats().base_struct)
        self.array('types', self.uint8, length=2)
        self.uint8('catchrate', default=255)
        self.uint8('baseexp')
        self.struct('ev', Stats(False).base_struct)
        self.array('items', self.uint16, length=2)
        self.uint8('gender')
        self.uint8('hatchcycle', default=1)
        self.uint8('basehappy', default=70)
        self.uint8('exprate')
        self.array('egggroups', self.uint8, length=2)
        self.array('abilities', self.uint8, length=2)
        self.uint8('flag')
        self.uint8('color')
        self.uint16('reserved')
        self.array('tmblock', self.uint32, length=4)

        if game.gen > 4:
            with self.replace('baseexp'):
                self.uint8('stage')
            with self.replace('items'):
                self.array('items', self.uint16, length=3)
            with self.replace('abilities'):
                self.array('abilities', self.uint8, length=3)
            with self.after('flag'):
                self.uint16('formeid')
                self.uint16('forme')
                self.uint8('numforms')
            with self.after('color'):
                self.uint16('baseexp')
                self.uint16('height')
                self.uint16('weight')
            self.remove('reserved')
            if game.idx < 2:
                self.array('tutorblock', self.uint32, length=1)
            else:
                self.array('tutorblock', self.uint32, length=5)
