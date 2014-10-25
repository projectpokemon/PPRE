
import os

from ntr.header_bin import HeaderBin as NTRHeaderBin
from ctr.header_bin import HeaderBin as CTRHeaderBin

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


class Game(object):

    def __init__(self):
        self.workspace = None
        self.header = None
        self.config = {}
        self.archives = {}

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
        finally:
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
        return game

    def get_personal(self, natid):
        return self.archives['personal'].files[natid]

    def set_personal(self, natid, data):
        self.archives['personal'].files[natid] = data

    def save(self):
        pass


class DPGame(Game):
    def __init__(self):
        super(DPGame, self).__init__()


class PtGame(DPGame):
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
