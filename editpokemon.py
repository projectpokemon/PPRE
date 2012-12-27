#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui 
from editdlg import EditDlg, EditWidget

import config
from language import translate
import pokeversion
from nds import narc, txt
from nds.fmt import dexfmt

files = pokeversion.pokemonfiles

class EditPokemon(EditDlg):
    wintitle = "Pokemon Editor"
    def __init__(self, parent=None):
        super(EditPokemon, self).__init__(parent)
        game = config.project["versioninfo"][0]
        self.personalfname = config.project["directory"]+"fs"+files[
            game]["Personal"]
        self.textfname = config.project["directory"]+"fs"+pokeversion.textfiles[
            game]["Main"]
        self.textnarc = narc.NARC(open(self.textfname, "rb").read())
        self.pokemonnames = self.getTextEntry("Pokemon")
        self.typenames = self.getTextEntry("Types")
        self.itemnames = self.getTextEntry("Items")
        self.abilitynames = self.getTextEntry("Abilities")
        self.chooser.addItems(self.pokemonnames)
        self.addEditableTab("Personal", dexfmt[game.lower()],
            self.personalfname, self.getPokemonWidget)
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
    
def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return
    EditPokemon(config.mw).show()