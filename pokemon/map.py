
import os

from generic.editable import XEditable as Editable
from pokemon.field.script import Script
from pokemon.field.encounters import Encounters
from pokemon.msgdata.msg import Text


class Map(Editable):
    def define(self, game):
        self.game = game
        if game < game.from_string('HeartGold'):
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

    def load_id(self, map_id):
        with open(os.path.join(self.game.files.directory, 'arm9.dec.bin'))\
                as handle:
            handle.seek(self.game.map_table+map_id*self.size())
            # data = handle.read(self.size())
            self.load(handle)
        if 0 and self.encounter_idx != 0xFFFF:
            self.encounter.load(self.game.get_encounter(self.encounter_idx))
        else:
            self.encounter.load('\x00'*self.encounter.size())
        self.text.load(self.game.get_text(self.text_idx))
        self.script.load_text(self.text)
        self.script.load(self.game.get_script(self.script_idx))
