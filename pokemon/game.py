
import functools
import json
import os

import ndstool
from compression import blz
from ctr import ctrtool
from ctr.header_bin import HeaderBin as CTRHeaderBin
from ntr.header_bin import HeaderBin as NTRHeaderBin
from ntr.narc import NARC
from ntr.overlay import OverlayTable
from ctr.garc import GARC
from util import cached_property, subclasses
from util import BinaryIO
from generic import Editable

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
        try:
            item.gen
        except:
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
    def define(self):
        self.name = 'Project'
        self.restrict('name')
        self.description = 'Description'
        self.restrict('description')
        self.version = 0.1
        self.restrict('version')
        self.output = 'edit.nds'
        self.restrict('output')


class Files(Editable):
    def define(self, directory):
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
        Editable.__init__(self)
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
    def from_workspace(cls, workspace, init=False):
        if 0:  # auto-documentation
            return DP()
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
        if init:
            game.init()
        return game

    def init(self):
        pass

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
        game = Game.from_workspace(workspace, True)
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
                if hasattr(data, 'save'):
                    data = data.save()
                if hasattr(data, 'getvalue'):
                    data = data.getvalue()
                if data is None:
                    raise RuntimeError('Did not return writable data')
                archive.files[fileid] = data
                self.save_archive(archive,
                                  getattr(self, name[4:]+'_archive_file'))
            return set_wrapper
        return object.__getattribute__(self, name)

    def text(self, file_id):
        from pokemon.msgdata.msg import Text
        return Text(self).load(self.get_text(file_id))

    def locale_text_id(self, key):
        return self.text_contents[REGION_CODES[self.region_code]][key]

    def map(self, map_id):
        from pokemon.map import Map
        m = Map(self)
        m.load_id(map_id)
        return m

    @cached_property
    def overlay_table(self):
        with self.open('header.bin') as header:
            reader = BinaryIO.adapter(header)
            reader.seek(0x24)
            entry = reader.readUInt32()
            ram_offset = reader.readUInt32()
            size = reader.readUInt32()
            reader.seek(0x54)
            overlay_count = reader.readUInt32() >> 5  # Size/sizeof(entry)
        with self.open('overarm9.dec.bin') as overarm:
            ovt = OverlayTable(overlay_count, reader=overarm)
        return ovt

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
    waza_archive_file = 'poketool/waza/waza_tbl.narc'
    baby_file = 'poketool/personal/pms.narc'
    encounter_archive_files = {
        'Diamond': 'fielddata/encountdata/d_enc_data.narc',
        'Pearl': 'fielddata/encountdata/p_enc_data.narc'}
    trades_archive_file = 'fielddata/pokemon_trade/fld_trade.narc'
    event_archive_file = 'fielddata/eventdata/zone_event_release.narc'
    area_data_archive_file = 'fielddata/areadata/area_data.narc'
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
    mmodel_archive_file = 'data/mmodel/mmodel.narc'

    load_info = 0x2000b68
    type_effectiveness_table = (11, 0x225e378-0x222d5c0)
    file_system_table = (-1, 0x021058a0-0x02000000)
    map_table = 0xeedbc
    commands_files = ('dp.json', )

    text_contents = {
        'US': {
            'map_names': 382,
            'type_names': 565,
            'ability_names': 552,
            'item_names': 344,
            'move_names': 588,
            'pokemon_names': 362,
            'species_names': 621,
            'trainer_class_names': 560,
            'trainer_names': 559
        },
    }


class Pt(DP):
    idx = 3
    versions = {'Platinum': 2}
    personal_archive_file = 'poketool/personal/pl_personal.narc'
    waza_archive_file = 'poketool/waza/pl_waza_tbl.narc'
    encounter_archive_file = 'fielddata/encountdata/pl_enc_data.narc'
    item_archive_file = 'itemtool/itemdata/pl_item_data.narc'
    commands_files = ('dp.json', 'pt.json')

    load_info = 0x02000ba0
    file_system_table = (-1, 0x02100498-0x02000000)

    text_contents = {
        'US': {
        }
    }


class HGSS(Game):
    idx = 3
    gen = 4
    versions = {'HeartGold': 3, 'SoulSilver': 4}
    evo_archive_file = 'a/0/3/4'
    personal_archive_file = 'a/0/0/2'
    exp_archive_file = 'a/0/0/3'
    waza_archive_file = 'a/0/1/1'
    wotbl_archive_file = 'a/0/3/3'
    encounter_archive_files = {
        'HeartGold': 'a/0/3/7',
        'SoulSilver': 'a/1/3/6'}
    event_archive_file = 'a/0/3/2'
    area_data_archive_file = 'a/0/4/2'
    land_data_archive_file = 'a/0/6/5'
    map_matrix_archive_file = 'a/0/4/1'
    mapname_file = 'fielddata/maptable/mapname.bin'
    script_archive_file = 'a/0/1/2'
    text_archive_file = 'a/0/2/7'
    mmodel_archive_file = 'a/0/8/1'
    partner_appearance_archive_file = 'a/1/4/1'

    load_info = 0x02000ba0
    type_effectiveness_table = (12, 0x226cc7c-0x22378c0)
    file_system_table = (-1, 0x0210f210-0x02000000)
    map_table = 0xf6be0
    following_sprite_table = (-1, 0x020ff088-0x02000000, 993, 428)
    overworld_sprite_table = (1, 0x22074a2-0x021e5900, 993)
    max_forme_table = (-1, 0x020fe8d0-0x02000000, 493)  # fe8d4-4
    gender_forme_table = (-1, 0x020fecaa-0x02000000, 493)  # fecae-4
    commands_files = ('hgss.json', )

    text_contents = {
        'US': {
            'map_names': 279,
            'type_names': 735,
            'ability_names': 720,
            'item_names': 222,
            'move_names': 750,
            'pokemon_names': 237,
            'species_names': 823,
            'trainer_class_names': 730,
            'trainer_names': 729
        },
    }

    def init(self):
        blz.decompress_arm9(self)
        blz.decompress_overlays(self)

        with open(os.path.join(self.files.directory, 'arm9.dec.bin'), 'r+')\
                as handle:
            """Breaks the while(AUXSPICNT != 80){} loop"""
            handle.seek(0xde16c)
            handle.write(chr(0)*4)
            handle.seek(0xd3fa8)
            handle.write(chr(0)*4)
            # handle.seek(0x1a570)
            # handle.write(chr(0)*2)


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

    load_info = 0x2004f70

    commands_files = ('bw.json', )

    def init(self):
        blz.decompress_arm9(self)
        blz.decompress_overlays(self)


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
    script_archive_file = 'a/0/1/1'

    def archive(self, filename):
        return GARC(open(os.path.join(self.files.directory, 'fs', filename)))


class ORAS(XY):
    idx = 2
    versions = {'OmegaRuby': 2, 'AlphaSapphire': 3}
    personal_archive_file = 'a/1/9/5'
    script_archive_file = 'a/0/1/3'
