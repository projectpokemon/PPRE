
import os
import re

from generic.editable import XEditable as Editable
from pokemon.field.script import Script
from pokemon.field.encounters import Encounters
from pokemon.game import Game
from pokemon.msgdata.msg import Text


class Map(Editable):
    def define(self, game):
        self.game = game
        if game < Game.from_string('HeartGold'):
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
        else:
            self.uint16('encounter_idx')
            self.uint16('u2')
            self.uint16('u4')
            self.uint16('script_idx')
            self.uint16('u8')
            self.uint16('text_idx')
            self.uint16('uc')
            self.uint16('ue')
            self.uint16('event_idx')
            self.uint16('u12')
            self.uint16('u14')
            self.uint16('u16')
        self.script = Script(game)
        self.encounter = Encounters(game)
        self.text = Text(game)
        self.names = self.get_names()

    def get_names(self):
        names = []
        self.location_text = self.game.text(self.game.locale_text_id('map_names'))
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
        if shallow:
            return
        if 0 and self.encounter_idx != 0xFFFF:
            self.encounter.load(self.game.get_encounter(self.encounter_idx))
        else:
            self.encounter.load('\x00'*self.encounter.size())
        self.text.load(self.game.get_text(self.text_idx))
        self.script.load_text(self.text)
        self.script.load(self.game.get_script(self.script_idx))
