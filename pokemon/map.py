
import os
import re

from generic.editable import XEditable as Editable
from pokemon.field.script import Script
from pokemon.field.encounters import Encounters
from pokemon.field.zone_events import ZoneEvents
from pokemon.game import Game
from pokemon.msgdata.msg import Text


class Map(Editable):
    def define(self, game):
        self.game = game
        if game <= Game.from_string('Platinum'):
            self.uint16('u0')
            self.uint16('u2')
            self.uint16('script_idx')
            self.uint16('u6')
            self.uint16('text_idx')
            self.uint16('ua')
            self.uint16('uc')
            self.uint16('encounter_idx')
            self.uint16('event_idx')
            self.uint16('u12')
            self.uint16('u14')
            self.uint16('u16')
        elif game <= Game.from_string('SoulSilver'):
            # chunks derived from 0203b290
            self.uint16('encounter_idx', width=8)
            self.uint16('u1', width=8)
            self.uint16('u2_0', width=4)
            self.uint16('u2_1', width=6)
            self.uint16('u2_2', width=6)
            self.uint16('matrix_idx')
            self.uint16('script_idx')
            self.uint16('u8')
            self.uint16('text_idx')
            self.uint16('uc')
            self.uint16('ue')
            self.uint32('event_idx', width=16)  # u32 needed to pack 0x10-0x13
            self.uint32('map_name', width=8)
            self.uint32('u12_1', width=4)
            self.uint32('u12_2', width=4)
            self.uint32('u14_0', width=1)  # 0
            self.uint32('u14_1', width=7)  # 1-7
            self.uint32('u14_2', width=4)  # 8-11
            self.uint32('u14_3', width=6)  # 12-17
            self.uint32('u14_4', width=2)  # 18-19
            self.uint32('u14_5', width=5)  # 20-24
            self.uint32('u14_6', width=1)  # 25
            self.uint32('u14_7', width=1)  # where is 26 used?
            self.uint32('u14_8', width=1)  # 27
            self.uint32('u14_9', width=1)  # 28
            self.uint32('u14_10', width=1)  # 29
            self.uint32('u14_11', width=1)  # 30
            self.uint32('u14_12', width=1)  # 31
        self.name = ''
        self.script = Script(game)
        self.encounter = Encounters(game)
        self.events = ZoneEvents(game)
        self.text = Text(game)
        self.names = self.game.text(self.game.locale_text_id('map_names'))
        self.code_names = self.get_code_names()

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
            handle.seek(self.game.map_table+map_id*self.size())
            # data = handle.read(self.size())
            self.load(handle)
        self.code_name = self.code_names[map_id]
        self.name = self.names[self.map_name]
        if shallow:
            return
        if 0 and self.encounter_idx != 0xFFFF:
            self.encounter.load(self.game.get_encounter(self.encounter_idx))
        else:
            self.encounter.load('\x00'*self.encounter.size())
        self.text.load(self.game.get_text(self.text_idx))
        self.script.load_text(self.text)
        self.script.load(self.game.get_script(self.script_idx))
        self.events.load(self.game.get_event(self.event_idx))
