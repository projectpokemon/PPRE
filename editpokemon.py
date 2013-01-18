#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, struct
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui 
from editdlg import EditDlg, EditWidget

import config
from language import translate
import pokeversion
from nds import narc, txt
from nds.fmt import dexfmt, evofmt

files = pokeversion.pokemonfiles

stats = ("hp", "atk", "def", "speed", "spatk", "spdef")

class EditEVs(EditWidget):
    def __init__(self, parent=None):
        super(EditEVs, self).__init__(EditWidget.NONE, parent)
        self.valuers = []
        x = 0
        y = 0
        for stat in stats:
            sb = EditWidget(EditWidget.SPINBOX, self)
            sb.setValues([0, 3])
            sb.setName(translate("pokemonstat_"+stat)+" EV")
            width, height = sb.getGeometry()
            sb.setGeometry(QRect(x, y, width, height))
            sb.changed = self._changed
            self.valuers.append(sb)
            y += height
        self.setGeometry(0, 0, width, y)
    def setValue(self, value):
        for i in range(6):
            self.valuers[i].setValue(value&3)
            value >>= 2
    def getValue(self):
        value = 0
        for i in range(6):
            value |= self.valuers[i].getValue()<<(i*2)
        return value
    def getGeometry(self):
        return (self.geometry().width(), self.geometry().height())
        
class EditTMs(EditWidget):
    def __init__(self, parent=None):
        super(EditTMs, self).__init__(EditWidget.TAB, parent)
        self.tabname = "TMs/HMs"
        self.valuers = []
        x = 0
        y = 0
        off = 0
        txt = "%s%%02i"%translate("pokemontm")
        if pokeversion.gens[config.project["versioninfo"][0]] == 4:
            tmmax = 92
        else:
            tmmax = 95
        for i in range(104):
            sb = EditWidget(EditWidget.CHECKBOX, self)
            if i == 60:
                x = width
                mheight = y
                y = 0
            elif i == tmmax:
                txt = "%s%%02i"%translate("pokemonhm")
                off = tmmax
            sb.setName(txt%(i-off+1))
            width, height = sb.getGeometry()
            sb.setGeometry(QRect(x, y, width, height))
            sb.changed = self._changed
            self.valuers.append(sb)
            y += height
        self.setGeometry(0, 0, width*2, mheight)
    def setValue(self, value):
        tmdata = struct.unpack("B"*13, value)
        for i, d in enumerate(tmdata):
            for j in range(8):
                idx = i*8+j
                self.valuers[idx].setValue((tmdata[i]>>j)&1)
    def getValue(self):
        values = []
        for i in range(13):
            values.append(0)
            for j in range(8):
                idx = i*8+j
                values[i] |= self.valuers[idx].getValue() << j
        return struct.pack("13B", *values)
        
class EditMoves(EditWidget):
    def __init__(self, size="H", parent=None):
        super(EditMoves, self).__init__(EditWidget.NONE, parent)
        self.datasize = size
        y = 0
        x = 25
        self.mover = EditWidget(EditWidget.COMBOBOX, self)
        self.mover.changed = self._changed
        width, height = self.mover.getGeometry()
        self.mover.setGeometry(QRect(x, y, width, height))
        y += height
        self.leveler = EditWidget(EditWidget.SPINBOX, self)
        self.leveler.changed = self._changed
        if self.datasize == "I":
            self.leveler.setValues([0, 0xFFFF])
        else:
            self.leveler.setValues([0, 0x7F])
        width, height = self.leveler.getGeometry()
        self.leveler.setGeometry(QRect(x, y, width, height))
        y += height
        self.deleter = QPushButton("X", self)
        self.deleter.setGeometry(0, 0, x, y)
        QObject.connect(self.deleter,
            QtCore.SIGNAL("pressed()"), self._remove)
        self.setGeometry(0, 0, x+width, y)
    def _remove(self):
        self.remove(self)
    def setName(self, name):
        self.mover.setName("Move")
        self.leveler.setName("Level")
    def setValue(self, value):
        if self.datasize == "I":
            self.mover.setValue(value&0xFFFF)
            self.leveler.setValue((value>>16)&0xFFFF)
        else:
            self.mover.setValue(value&0x1FF)
            self.leveler.setValue((value>>9)&0x7F)
    def getValue(self):
        if self.datasize == "I":
            value = (self.leveler.getValue()<<16) | (self.mover.getValue())
        else:
            value = (self.leveler.getValue()<<9) | (self.mover.getValue())
        return value
    def getGeometry(self):
        return (self.geometry().width(), self.geometry().height())
    def __lt__(self, other):
        if isinstance(other, EditMoves):
            return self.leveler.getValue() < other.leveler.getValue()
        return self.getValue() < other.getValue()

def moveTerminator(data, length):
    if data&0xFFFF == 0xFFFF:
        return True
    if length > 20:
        return True
    return False

class EditPokemon(EditDlg):
    wintitle = "Pokemon Editor"
    def __init__(self, parent=None):
        super(EditPokemon, self).__init__(parent)
        game = config.project["versioninfo"][0]
        self.personalfname = config.project["directory"]+"fs"+files[
            game]["Personal"]
        self.evolutionfname = config.project["directory"]+"fs"+files[
            game]["Evolution"]
        self.lvlmovesfname = config.project["directory"]+"fs"+files[
            game]["Moves"]
        self.pokemonnames = self.getTextEntry("Pokemon")
        self.typenames = self.getTextEntry("Types")
        self.itemnames = self.getTextEntry("Items")
        self.abilitynames = self.getTextEntry("Abilities")
        self.movenames = self.getTextEntry("Moves")
        self.chooser.addItems(self.pokemonnames)
        self.addEditableTab("Personal", dexfmt[game.lower()],
            self.personalfname, self.getPokemonWidget)
        self.addEditableTab("Evolution", evofmt[game.lower()],
            self.evolutionfname, self.getEvolutionWidget)
        if pokeversion.gens[game] == 5:
            movefmt = ["I", "move %i"]
            terminate = struct.pack("I", 0xFFFFFFFF)
        else:
            movefmt = ["H", "move %i"]
            terminate = struct.pack("H", 0xFFFF)
        self.addListableTab("Moveset", movefmt, self.lvlmovesfname, 
            moveTerminator, terminate, self.getMoveWidget)
        self.addTextTab("Flavor", self.getFlavorEntries, self.getFlavorEntry, 
            self.getFlavorWidget)
    def getTextEntry(self, entry):
        version = config.project["versioninfo"]
        entrynum = pokeversion.textentries[version[0]][pokeversion.langs[
            version[1]]][entry]
        if pokeversion.gens[version[0]] == 4:
            text = txt.gen4get(self.textnarc.gmif.files[entrynum])
        elif pokeversion.gens[version[0]] == 5:
            text = txt.gen5get(self.textnarc.gmif.files[entrynum])
        else:
            raise ValueError
        ret = []
        for t in text:
            ret.append(t[1])
        return ret
    def getPokemonWidget(self, name, size, parent):
        choices = None
        if name[:4] == "type":
            choices = self.typenames
        elif name[:4] == "item":
            choices = self.itemnames
        elif name[:7] == "ability":
            choices = self.abilitynames
        elif name[:8] == "egggroup":
            choices = translate("pokemonegggroups")
        elif name == "evs":
            return EditEVs(parent)
        elif name == "tms":
            return EditTMs(None)
        elif name in ("exprate", "color"):
            choices = translate("pokemon"+name+"s")
        if choices:
            cb = EditWidget(EditWidget.COMBOBOX, parent)
            cb.setValues(choices)
            cb.setName(translate(name))
            return cb
        sb = EditWidget(EditWidget.SPINBOX, parent)
        if size == 'H':
            sb.setValues([0, 0xFFFF])
        else:
            sb.setValues([0, 0xFF])
        sb.setName(translate(name))
        return sb
    def getEvolutionWidget(self, name, size, parent):
        choices = None
        if name[:6] == "method":
            choices = translate("pokemonevolutionmethods")
        elif name[:6] == "target":
            choices = self.pokemonnames
        if choices:
            cb = EditWidget(EditWidget.COMBOBOX, parent)
            cb.setValues(choices)
            cb.setName(translate(name))
            return cb
        sb = EditWidget(EditWidget.SPINBOX, parent)
        sb.setValues([0, 0xFFFF])
        sb.setName(translate(name))
        return sb
    def getMoveWidget(self, name, size, parent):
        w = EditMoves(size, parent)
        w.mover.setValues(self.movenames)
        w.setName(name)
        return w
    def getFlavorEntries(self):
        version = config.project["versioninfo"]
        texts = pokeversion.textentries[version[0]][
                    pokeversion.langs[version[1]]]
        ret = []
        ret.append(("names", texts["PokemonNames"].keys()))
        ret.append(("flavor", sorted(texts["Flavor"].keys())))
        return ret
    def getFlavorEntry(self, section, name, i):
        version = config.project["versioninfo"]
        texts = pokeversion.textentries[version[0]][
                    pokeversion.langs[version[1]]]
        if section == "flavor":
            return (texts["Flavor"][name], "0_"+str(i))
        return (texts["PokemonNames"][name], "0_"+str(i))
    def getFlavorWidget(self, section, name, parent):
        if section == "flavor":
            te = EditWidget(EditWidget.TEXTEDIT, parent)
            te.setName(translate(name))
            return te
        le = EditWidget(EditWidget.LINEEDIT, parent)
        le.setName(translate(name))
        return le
        

def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return
    EditPokemon(config.mw).show()