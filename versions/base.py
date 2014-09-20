
import os

from rawdb.nds.narc import NARC
from rawdb.util import cached_property
from rawdb.elements.base_stats import BaseStats
from rawdb.elements.evolutions import Evolutions
from rawdb.elements.level_moves import LevelMoves


class GameVersion(object):
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def archive(self, filename):
        data = open(os.path.join(self.base_dir, filename), 'rb').read()
        return NARC(data)

    @cached_property
    def pokemon(self):
        return BaseStats(self)

    @cached_property
    def evolutions(self):
        return Evolutions(self)

    @cached_property
    def level_moves(self):
        return LevelMoves(self)
