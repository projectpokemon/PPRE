
import abc
import os

from ctr.header_bin import HeaderBin as CTRHeaderBin
from ntr.header_bin import HeaderBin as NTRHeaderBin
from ntr.narc import NARC
from util import cached_property

GAME_CODES = {
    'ADA': 'Diamond',
    'APA': 'Pearl',
    'CPU': 'Platinum',
    'IPK': 'HeartGold',
    'IPG': 'SoulSilver',
    'IRB': 'Black',
    'IRA': 'White',
    'IRE': 'Black2',
    'IRD': 'White2',
    'EKJ': 'X',
    'EK2': 'Y',
    'ECR': 'OmegaRuby',
    'ECL': 'AlphaSapphire'
}

REGION_CODES = {
    'E': 'US',
    'O': 'US',
    'J': 'JP',
    'A': 'EU',
    'P': 'EU',
    'K': 'KO'
}

GEN_IV = ('Diamond', 'Pearl', 'Platinum', 'HeartGold', 'SoulSilver')
GEN_V = ('Black', 'White', 'Black2', 'White2')
GEN_VI = ('X', 'Y', 'OmegaRuby', 'AlphaSapphire')


class Game(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.workspace = None
        self.game_name = None
        self.game_code = None
        self.region_code = None
        self.header = None
        self.config = {}

    @staticmethod
    def from_workspace(workspace):
        try:
            # NTR
            handle = open(os.path.join(workspace, 'header.bin'))
        except:
            # CTR
            with open(os.path.join(workspace, 'ncch_header.bin')) as handle2:
                header = CTRHeaderBin(handle2)
        else:
            header = NTRHeaderBin(handle)
            handle.close()
        game_code = header.base_code[:3]
        region_code = header.base_code[3]
        try:
            game_name = GAME_CODES[game_code]
        except:
            raise ValueError('Unknown game code: '+game_code)
        if game_name in ('Diamond', 'Pearl'):
            game = DPGame()
        elif game_name == 'Platinum':
            game = PtGame()
        elif game_name in ('HeartGold', 'SoulSilver'):
            game = HGSSGame()
        elif game_name in ('Black', 'White'):
            game = BWGame()
        elif game_name in ('Black2', 'White2'):
            game = B2W2Game()
        elif game_name in ('X', 'Y'):
            game = XYGame()
        elif game_name in ('OmegaRuby', 'AlphaSapphire'):
            game = ORASGame()
        game.workspace = workspace
        game.game_name = game_name
        game.game_code = game_code
        game.region_code = region_code
        game.header = header
        return game

    def archive(self, filename):
        return NARC(open(os.path.join(self.workspace, 'fs', filename)))

    @cached_property
    def personal_archive(self):
        return self.archive(self.personal_archive_file)

    def get_personal(self, natid):
        return self.personal_archive.files[natid]

    def set_personal(self, natid, data):
        self.personal_archive.files[natid] = data

    def save(self):
        pass


class DPGame(Game):
    personal_archive_file = 'poketool/personal/personal.narc'

    def __init__(self):
        super(DPGame, self).__init__()


class PtGame(DPGame):
    personal_archive_file = 'poketool/personal/pl_personal.narc'

    def __init__(self):
        super(PtGame, self).__init__()


class HGSSGame(Game):
    def __init__(self):
        super(HGSSGame, self).__init__()


class BWGame(Game):
    def __init__(self):
        super(BWGame, self).__init__()


class B2W2Game(Game):
    def __init__(self):
        super(B2W2Game, self).__init__()


class XYGame(Game):
    def __init__(self):
        super(XYGame, self).__init__()


class ORASGame(XYGame):
    def __init__(self):
        super(ORASGame, self).__init__()
