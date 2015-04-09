
import functools
import json
import os

import ndstool
from compression import blz
from ctr import ctrtool
from ctr.header_bin import HeaderBin as CTRHeaderBin
from ntr.header_bin import HeaderBin as NTRHeaderBin
from ntr.narc import NARC
from ctr.garc import GARC
from util import cached_property, subclasses
from util import BinaryIO
from generic.editable import Editable

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


@functools.total_ordering
class Version(object):
    idx = None
    gen = None

    def __init__(self, gen=4, idx=None):
        self.gen = gen
        self.idx = idx

    def __eqx__(self, other):
        if self.gen != other.gen:
            return False
        if self.idx is None or other.idx is None:
            return True
        return self.idx == other.idx

    def __lt__(self, other):
        if self.gen < other.gen:
            return True
        elif self.gen > other.gen:
            return False
        return self.idx < other.idx

    def __gt__(self, other):
        return not self.__lt__(other) and not self.__eqx__(other)

    def __contains__(self, item):
        if not isinstance(item, Version):
            item = Version.from_string(item)
        return self.__eqx__(item)

    @staticmethod
    def from_string(name):
        try:
            idx = ['Diamond', 'Pearl', 'Platinum',
                   'HeartGold', 'SoulSilver'].index(name)
            gen = 4
        except (ValueError, IndexError):
            try:
                idx = ['Black', 'White', 'Black2', 'White2'].index(name)
                gen = 5
            except (ValueError, IndexError):
                try:
                    idx = ['X', 'Y', 'OmegaRuby', 'AlphaSapphire'].index(name)
                    gen = 6
                except (ValueError, IndexError):
                    raise ValueError('Unknown version: {0}'.format(name))
        return Version(gen, idx)


GEN_IV = Version(4)
GEN_V = Version(5)
GEN_VI = Version(6)

GAME_COLORS = {
    'Diamond': '#89d1e5',  # 'rgb(133, 218, 239)'
    'Pearl': '#d1b3b9',
    'Platinum': '#E5E4E2',
    'HeartGold': '#FDD017',
    'SoulSilver': '#C0C0C0',
    'Black': '#000000',
    'White': '#ffffff',
    'Black2': '#000000',
    'White2': '#ffffff',
    'X': '#6176b5',
    'Y': '#ff251d',
    'OmegaRuby': '#9B111E',
    'AlphaSapphire': '#0F52BA'
}


class Project(Editable):
    def __init__(self):
        self.name = 'Project'
        self.restrict('name')
        self.description = 'Description'
        self.restrict('description')
        self.version = 0.1
        self.restrict('version')
        self.output = 'edit.nds'
        self.restrict('output')


class Files(Editable):
    def __init__(self, directory):
        self.base = ''
        self.restrict('base')
        self.directory = directory
        self.restrict('directory')


class Game(Editable, Version):
    """A Loaded Game Instance

    """
    versions = {'': 0}
    commands_files = ()

    def __init__(self):
        self.files = None
        self.restrict('files')
        self.project = Project()
        self.restrict('project')
        self.game_name = None
        self.game_code = None
        self.region_code = None
        self.color = '#E5E4E2'
        self.header = None
        self.config = {}

    @classmethod
    def from_workspace(cls, workspace):
        files = Files(workspace)
        try:
            # NTR
            handle = open(os.path.join(files.directory, 'header.bin'))
        except:
            # CTR
            with open(os.path.join(files.directory, 'ncch_header.bin')) as handle2:
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
        for game_cls in subclasses(cls, recursive=True):
            if game_name in game_cls.versions:
                game = game_cls()
                game.idx = game_cls.versions[game_name]
                break
        else:
            game = game_cls()
            game.idx = min(game_cls.versions.values())
        game.files = files
        game.game_name = game_name
        game.game_code = game_code
        game.region_code = region_code
        game.color = GAME_COLORS[game_name]
        game.header = header
        game.load_config()
        if game < GEN_VI:
            blz.decompress_arm9(game)
        return game

    @staticmethod
    def from_file(filename, workspace, **kwargs):
        """Creates a workspace from a ROM

        Returns
        -------
        game : Game
        """
        tail = os.path.split(filename)[1]
        name, ext = os.path.splitext(tail)
        ext = ext.lower()
        if ext in ('.3ds', '.3dz'):
            ctrtool.dump(filename, workspace, xorpad=kwargs.pop('xorpad'))
        elif ext == '.nds':
            ndstool.dump(filename, workspace)
        else:
            raise ValueError('Not able to detect file type')
        game = Game.from_workspace(workspace)
        game.write_config()
        return game

    def to_file(self, filename=None):
        """Exports workspace to a built ROM

        Parameters
        ----------
        filename : string
            If provided, the filename will be used. If not, the project's
            default output filename will be used
        """
        if filename is None:
            filename = os.path.join(self.files.directory, self.project.output)
        if self < GEN_VI:
            ndstool.build(filename, self.files.directory)
        else:
            # TODO: ctrtool build
            ctrtool.build(filename, self.files.directory)

    def load_config(self):
        try:
            with open(os.path.join(self.files.directory, 'config.json'))\
                    as handle:
                self.from_dict(json.load(handle))
        except IOError as err:
            print(err)

    def write_config(self):
        with open(os.path.join(self.files.directory, 'config.json'), 'w')\
                as handle:
            json.dump(self.to_dict(), handle)

    def open(self, *parts, **kwargs):
        """Open a file relative to this workspace

        Parameters
        ----------
        *parts : *string
            File parts to be joined (by directory separator
        mode : string
            Mode to open file as
        """
        mode = kwargs.get('mode', 'r')
        return open(os.path.join(os.path.dirname(__file__), '..',
                                 self.files.directory, *parts), mode)

    def archive(self, filename):
        return NARC(open(os.path.join(self.files.directory, 'fs', filename)))

    def save_archive(self, archive, filename):
        with open(os.path.join(self.files.directory, 'fs', filename), 'wb')\
                as handle:
            archive.save(BinaryIO.adapter(handle))

    def __getattr__(self, name):
        if name[-8:] == '_archive':
            try:
                fnames = getattr(self, name+'_files')
                fname = fnames[self.game_name]
            except (AttributeError, KeyError):
                fname = getattr(self, name+'_file')
            return self.archive(fname)
        elif name[:4] == 'get_':
            def get_wrapper(fileid):
                return getattr(self, name[4:]+'_archive').files[fileid]
            return get_wrapper
        elif name[:4] == 'set_':
            def set_wrapper(fileid, data):
                archive = getattr(self, name[4:]+'_archive')
                archive.files[fileid] = data
                self.save_archive(archive, getattr(self, name+'_archive_file'))
            return set_wrapper
        return object.__getattribute__(self, name)

    def text(self, file_id):
        from pokemon.msgdata.msg import Text
        return Text(self).load(self.get_text(file_id))

    @cached_property
    def personal_archive(self):
        return self.archive(self.personal_archive_file)

    def get_personal(self, natid):
        return self.personal_archive.files[natid]

    def set_personal(self, natid, data):
        self.personal_archive.files[natid] = data
        self.save_archive(self.personal_archive, self.personal_archive_file)

    @cached_property
    def evo_archive(self):
        return self.archive(self.evo_archive_file)

    def get_evo(self, natid):
        return self.evo_archive.files[natid]

    def set_evo(self, natid, data):
        self.evo_archive.files[natid] = data
        self.save_archive(self.evo_archive, self.evo_archive_file)

    @cached_property
    def wotbl_archive(self):
        return self.archive(self.wotbl_archive_file)

    def get_wotbl(self, natid):
        return self.wotbl_archive.files[natid]

    def set_wotbl(self, natid, data):
        self.wotbl_archive.files[natid] = data
        self.save_archive(self.wotbl_archive, self.wotbl_archive_file)

    def save(self):
        pass


class DP(Game):
    gen = 4
    idx = 0
    versions = {'Diamond': 0, 'Pearl': 1}
    evo_archive_file = 'poketool/personal/evo.narc'
    personal_archive_file = 'poketool/personal/personal.narc'
    wotbl_archive_file = 'poketool/personal/wotbl.narc'
    pokemon_data_archive_file = personal_archive_file
    level_moves_archive_file = wotbl_archive_file

    exp_archive_file = 'poketool/personal/growtbl.narc'
    move_data_archive_file = 'poketool/waza/waza_tbl.narc'
    baby_file = 'poketool/personal/pms.narc'
    encounter_archive_files = {
        'Diamond': 'fielddata/encountdata/d_enc_data.narc',
        'Pearl': 'fielddata/encountdata/p_enc_data.narc'}
    trades_archive_file = 'fielddata/pokemon_trade/fld_trade.narc'
    event_archive_file = 'fielddata/eventdata/zone_event_release.narc'
    map_archive_file = 'fielddata/areadata/area_data.narc'
    land_data_archive_file = 'fielddata/land_data/land_data_release.narc'
    map_matrix_archive_file = 'fielddata/mapmatrix/map_matrix.narc'
    mapname_file = 'fielddata/maptable/mapname.bin'
    script_archive_file = 'fielddata/script/scr_seq_release.narc'
    item_archive_file = 'itemtool/itemdata/item_data.narc'
    berry_archive_file = 'itemtool/itemdata/nuts_data.narc'
    text_archive_file = 'msgdata/msg.narc'
    trainer_archive_file = 'poketool/trainer/trdata.narc'
    trainer_pokemon_archive_file = 'poketool/trainer/trpoke.narc'
    battle_tower_trainer_archive_file = 'battle/b_tower/btdtr.narc'
    battle_tower_trainer_pokemon_archive_file = 'battle/b_tower/btdpm.narc'

    load_info = 0x2000b68
    commands_files = ('dp.json', )


class Pt(DP):
    idx = 3
    versions = {'Platinum': 2}
    personal_archive_file = 'poketool/personal/pl_personal.narc'
    encounter_archive_file = 'fielddata/encountdata/pl_enc_data.narc'
    item_archive_file = 'itemtool/itemdata/pl_item_data.narc'
    commands_files = ('dp.json', 'pt.json')


class HGSS(Game):
    idx = 3
    gen = 4
    versions = {'HeartGold': 3, 'SoulSilver': 4}
    evo_archive_file = 'a/0/3/4'
    personal_archive_file = 'a/0/0/2'
    exp_archive_file = 'a/0/0/3'
    wotbl_archive_file = 'a/0/3/3'
    encounter_archive_files = {
        'HeartGold': 'a/0/3/7',
        'SoulSilver': 'a/1/3/6'}

    load_info = 0x02000ba0
    commands_files = ('hgss.json', )


class BW(Game):
    idx = 0
    gen = 5
    versions = {'Black': 0, 'White': 1}
    evo_archive_file = 'a/0/1/9'
    personal_archive_file = 'a/0/1/6'
    wotbl_archive_file = 'a/0/1/8'
    exp_archive_file = 'a/0/1/7'
    encounter_archive_file = 'a/1/2/6'
    item_archive_file = 'a/0/2/4'
    menu_archive_file = 'a/0/0/2'
    text_archive_file = 'a/0/0/3'

    commands_files = ('bw.json', )


class B2W2(BW):
    idx = 2
    versions = {'Black2': 2, 'White2': 3}
    encounter_archive_file = 'a/1/2/7'

    load_info = 0x2004fb0

    commands_files = ('bw.json', 'b2w2.json')


class XY(Game):
    idx = 0
    gen = 6
    versions = {'X': 0, 'Y': 1}
    evo_archive_file = 'a/2/1/5'
    personal_archive_file = 'a/2/1/8'
    wotbl_archive_file = 'a/2/1/4'

    def archive(self, filename):
        return GARC(open(os.path.join(self.files.directory, 'fs', filename)))


class ORAS(XY):
    idx = 2
    versions = {'OmegaRuby': 2, 'AlphaSapphire': 3}
    personal_archive_file = 'a/1/9/5'
