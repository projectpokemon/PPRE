
import os
import re

from generic.editable import XEditable as Editable
from pokemon.field.script import Script, ScriptConditions
from pokemon.field.encounters import Encounters
from pokemon.field.zone_events import ZoneEvents
from pokemon.field.area.area_data import AreaData
from pokemon.game import Game
from pokemon.msgdata.msg import Text


class Map(Editable):
    WEATHER_NONE = 0
    WEATHER_RAIN = 1  # 1-3
    WEATHER_SNOW_LIGHT = 4
    WEATHER_SNOW = 5  # 4-8
    WEATHER_DIAMOND_SNOW = 8
    WEATHER_FOG = 9
    WEATHER_DARK = 11
    WEATHER_DIM = 13

    def define(self, game):
        self.game = game
        if game <= Game.from_string('Platinum'):
            self.uint16('u0_0', width=8)
            self.uint16('area_data_idx', width=8)
            self.uint16('matrix_idx')
            self.uint16('script_idx')
            self.uint16('script_condition_idx')
            self.uint16('text_idx', default=0)
            self.uint16('music_orig_idx')
            self.uint16('music_copy_idx')  # Actually differs here?
            self.uint16('encounter_idx')
            self.uint16('event_idx')
            self.uint16('map_name')
            self.uint16('u14')
            self.uint16('u16')
            self.no_encounters = 0xFFFF
        elif game <= Game.from_string('SoulSilver'):
            # chunks derived from 0203b290
            self.uint16('encounter_idx', default=0xFF, width=8)
            self.uint16('area_data_idx', width=8)
            self.uint16('u2_0', width=4)
            self.uint16('u2_1', width=6)
            self.uint16('u2_2', width=6)
            self.uint16('matrix_idx')
            self.uint16('script_idx')
            self.uint16('script_condition_idx')
            self.uint16('text_idx', default=3)
            self.uint16('music_orig_idx')
            self.uint16('music_copy_idx')
            self.uint32('event_idx', width=16)  # u32 needed to pack 0x10-0x13
            self.uint32('map_name', width=8)
            self.uint32('map_sign_background', width=4)
            self.uint32('u12_2', width=4)
            self.uint32('region', width=1)  # 0
            self.uint32('weather', width=7)  # 1-7
            self.uint32('map_sign_control', width=4)  # 8-11
            self.uint32('map_view_angle', width=6)  # 12-17
            self.uint32('following_allowed', width=2)  # 18-19, 1 = small, 2 = any
            self.uint32('battle_background', width=5)  # 20-24, ??
            self.uint32('can_bike', width=1)  # 25
            self.uint32('is_map_used', width=1, default=1)  # 26, discarded maps=0
            self.uint32('can_escape_rope', width=1)  # 27, or dig
            self.uint32('can_fly', width=1)  # 28
            self.uint32('circle_focus', width=1)  # 29, dark ring shows around outside of map
            self.uint32('u14_11', width=1)  # 30
            self.uint32('u14_12', width=1)  # 31
            self.no_encounters = 0xFF
        self.name = ''
        self.script = Script(game)
        self.script_conditions = ScriptConditions(game)
        self.encounters = Encounters(game)
        self.events = ZoneEvents(game)
        self.text = Text(game)
        self.area_data = AreaData()
        self.names = self.game.text(self.game.locale_text_id('map_names'))
        self.code_names = self.get_code_names()

    @property
    def music_idx(self):
        return self.music_orig_idx

    @music_idx.setter
    def music_idx(self, value):
        # There are absolutely no instances where these differ
        self.music_orig_idx = value
        self.music_copy_idx = value

    def get_code_names(self):
        names = []
        with self.game.open('fs', self.game.mapname_file) as handle:
            while True:
                try:
                    code = handle.read(16).strip(chr(0))
                    if not code:
                        break
                except:
                    break
                match = re.match(
                    '([CTDLRWP])([0-9]{2})(PC|FS|GYM|R)?'
                    '([0-9]{2})?([0-9]{2})?', code)
                if match is None:
                    names.append(code)
                    continue
                names.append('{type} {loc_id}: {subtype} {sub_id}-{sub_id2}'
                             .format(type=match.group(1),
                                     loc_id=match.group(2),
                                     subtype=match.group(3),
                                     sub_id=match.group(4),
                                     sub_id2=match.group(5)))
        return names

    def load_id(self, map_id, shallow=False):
        with open(os.path.join(self.game.files.directory, 'arm9.dec.bin'))\
                as handle:
            handle.seek(self.game.map_table+map_id*self.get_size())
            # data = handle.read(self.get_size())
            self.load(handle)
        self.code_name = self.code_names[map_id]
        self.name = self.names[self.map_name]
        if not shallow:
            self.full_load()

    def full_load(self):
        if self.encounter_idx != self.no_encounters:
            self.encounters.load(self.game.get_encounter(self.encounter_idx))
        else:
            self.encounters.load('\x00'*self.encounters.get_size())
        self.text.load(self.game.get_text(self.text_idx))
        self.area_data.load(self.game.get_area_data(self.area_data_idx))
        self.script.load_text(self.text)
        self.script_conditions.load(self.game.get_script(self.script_condition_idx))
        self.script.load(self.game.get_script(self.script_idx))
        self.events.load(self.game.get_event(self.event_idx))

    def commit(self, map_id, shallow=False):
        with open(os.path.join(self.game.files.directory, 'arm9.dec.bin'),
                  mode='r+') as handle:
            handle.seek(self.game.map_table+map_id*self.get_size())
            self.save(handle)
        if shallow:
            return
        if self.name != self.names[self.map_name]:
            self.names[self.map_name] = self.name
            self.game.set_text(self.game.locale_text_id('map_names'),
                               self.names)
        # TODO: codename?
        self.game.set_text(self.text_idx, self.text)
        self.game.set_area_data(self.area_data_idx, self.area_data)
        self.game.set_script(self.script_idx, self.script)
        self.game.set_script(self.script_condition_idx, self.script_conditions)
        self.game.set_event(self.event_idx, self.events)
        if self.encounter_idx != self.no_encounters:
            self.game.set_encounter(self.encounter_idx, self.encounters)
