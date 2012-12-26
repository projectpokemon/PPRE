#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import struct
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

import config
from language import translations
import pokeversion
from nds import narc, txt

files = pokeversion.pokemonfiles

stats = ("hp", "atk", "def", "speed", "spatk", "spdef")

wintitle = "%s - Pokemon Editor - PPRE"

class EditPokemon(QMainWindow):
    def __init__(self, parent=None):
        super(EditPokemon, self).__init__(parent)
        self.opening = True
        self.personalfname = config.project["directory"]+"fs"+files[
            config.project["versioninfo"][0]]["Personal"]
        self.textfname = config.project["directory"]+"fs"+pokeversion.textfiles[
            config.project["versioninfo"][0]]["Main"]
        self.textnarc = narc.NARC(open(self.textfname, "rb").read())
        self.pokemonnames = self.getTextEntry("Pokemon")
        self.typenames = self.getTextEntry("Types")
        self.itemnames = self.getTextEntry("Items")
        self.abilitynames = self.getTextEntry("Abilities")
        self.setupUi()
        self.dirty = False
        self.opening = False
    def setupUi(self):
        self.setObjectName("EditPokemon")
        self.setWindowTitle(wintitle%"No file opened")
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translations["menu_file"])
        self.menubar.addAction(self.menus["file"].menuAction())
        self.menutasks = {}
        self.menutasks["newpokemon"] = QAction(self.menus["file"])
        self.menutasks["newpokemon"].setText(translations["menu_newpokemon"])
        self.menus["file"].addAction(self.menutasks["newpokemon"])
        QObject.connect(self.menutasks["newpokemon"],
            QtCore.SIGNAL("triggered()"), self.newPokemon)
        self.menutasks["savepokemon"] = QAction(self.menus["file"])
        self.menutasks["savepokemon"].setText(translations["menu_savepokemon"])
        self.menus["file"].addAction(self.menutasks["savepokemon"])
        QObject.connect(self.menutasks["savepokemon"],
            QtCore.SIGNAL("triggered()"), self.savePokemon)
        self.menutasks["close"] = QAction(self.menus["file"])
        self.menutasks["close"].setText(translations["menu_close"])
        self.menus["file"].addAction(self.menutasks["close"])
        QObject.connect(self.menutasks["close"],
            QtCore.SIGNAL("triggered()"), self.quit)
        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.pokemonlist = QComboBox(self.widgetcontainer)
        self.pokemonlist.setGeometry(QRect(50, 25, 200, 20))
        for p in self.pokemonnames:
            self.pokemonlist.addItem(p[1])
        QObject.connect(self.pokemonlist,
            QtCore.SIGNAL("currentIndexChanged(int)"), self.openPokemon)
        self.tabcontainer = QTabWidget(self.widgetcontainer)
        self.tabcontainer.setGeometry(QRect(25, 50, 550, 300))
        self.generaltab = QWidget(self.tabcontainer)
        self.tabcontainer.addTab(self.generaltab, 
            translations["pokemontab_general"])
        self.natid = QLabel(self.generaltab)
        self.natid.setGeometry(QRect(10, 10, 50, 25))
        version = config.project["versioninfo"]
        if pokeversion.gens[version[0]] == 4:
            itemcount = 2
        elif pokeversion.gens[version[0]] == 5:
            itemcount = 3
        self.fieldcont = {}
        x = 10
        y = 40
        self.fieldcont["statlabelbase"] = QLabel(self.generaltab)
        self.fieldcont["statlabelbase"].setGeometry(QRect(x+30, y, 30, 20))
        self.fieldcont["statlabelbase"].setText(translations["pokemonstatbase"])
        self.fieldcont["statlabelev"] = QLabel(self.generaltab)
        self.fieldcont["statlabelev"].setGeometry(QRect(x+80, y, 30, 20))
        self.fieldcont["statlabelev"].setText(translations["pokemonstatev"])
        y += 25
        for stat in stats:
            self.fieldcont["statlabel_"+stat] = QLabel(self.generaltab)
            self.fieldcont["statlabel_"+stat].setGeometry(QRect(x, y, 30, 20))
            self.fieldcont["statlabel_"+stat].setText(
                translations["pokemonstat_"+stat]+": ")
            self.fieldcont["stat_"+stat] = QSpinBox(self.generaltab)
            self.fieldcont["stat_"+stat].setGeometry(QRect(x+30, y, 50, 20))
            self.fieldcont["stat_"+stat].setRange(0, 255)
            QObject.connect(self.fieldcont["stat_"+stat],
                QtCore.SIGNAL("valueChanged(int)"), self.changed)
            self.fieldcont["ev_"+stat] = QSpinBox(self.generaltab)
            self.fieldcont["ev_"+stat].setGeometry(QRect(x+80, y, 50, 20))
            self.fieldcont["ev_"+stat].setRange(0, 3)
            QObject.connect(self.fieldcont["ev_"+stat],
                QtCore.SIGNAL("valueChanged(int)"), self.changed)
            y += 25
        for field in ["catchrate", "baseexp"]:
            self.fieldcont["flabel_"+field] = QLabel(self.generaltab)
            self.fieldcont["flabel_"+field].setGeometry(QRect(x, y, 80, 20))
            self.fieldcont["flabel_"+field].setText(
                translations["pokemon"+field]+": ")
            self.fieldcont["f_"+field] = QSpinBox(self.generaltab)
            self.fieldcont["f_"+field].setGeometry(QRect(x+80, y, 50, 20))
            self.fieldcont["f_"+field].setRange(0, 255)
            QObject.connect(self.fieldcont["f_"+field],
                QtCore.SIGNAL("valueChanged(int)"), self.changed)
            y += 25
        y = 15
        x += 150
        for field in ["gender", "hatchcycle", "basehappy", "flee"]:
            self.fieldcont["flabel_"+field] = QLabel(self.generaltab)
            self.fieldcont["flabel_"+field].setGeometry(QRect(x, y, 80, 20))
            self.fieldcont["flabel_"+field].setText(
                translations["pokemon"+field]+": ")
            self.fieldcont["f_"+field] = QSpinBox(self.generaltab)
            self.fieldcont["f_"+field].setGeometry(QRect(x+80, y, 50, 20))
            self.fieldcont["f_"+field].setRange(0, 255)
            QObject.connect(self.fieldcont["f_"+field],
                QtCore.SIGNAL("valueChanged(int)"), self.changed)
            y += 25
        y = 15
        x += 150
        for field in ["exprate", "color"]:
            l = "flabel_"+field
            self.fieldcont[l] = QLabel(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x, y, 50, 20))
            self.fieldcont[l].setText(translations["pokemon"+field]+":")
            l = "f_"+field
            self.fieldcont[l] = QComboBox(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x+50, y, 100, 20))
            self.fieldcont[l].addItems(translations["pokemon"+field+"s"])
            QObject.connect(self.fieldcont[l],
                QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
            y += 25
        for i in range(2):
            l = "typelabel_"+str(i)
            self.fieldcont[l] = QLabel(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x, y, 50, 20))
            self.fieldcont[l].setText("%s %i: "%(
                translations["pokemontype"], i+1))
            l = "type_"+str(i)
            self.fieldcont[l] = QComboBox(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x+50, y, 100, 20))
            for t in self.typenames:
                self.fieldcont[l].addItem(t[1])
            QObject.connect(self.fieldcont[l],
                QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
            y += 25
        for i in range(itemcount):
            l = "itemlabel_"+str(i)
            self.fieldcont[l] = QLabel(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x, y, 50, 20))
            self.fieldcont[l].setText("%s %i: "%(
                translations["pokemonitem"], i+1))
            l = "item_"+str(i)
            self.fieldcont[l] = QComboBox(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x+50, y, 100, 20))
            for t in self.itemnames:
                self.fieldcont[l].addItem(t[1])
            QObject.connect(self.fieldcont[l],
                QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
            y += 25
        for i in range(2):
            l = "egggrouplabel_"+str(i)
            self.fieldcont[l] = QLabel(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x, y, 50, 20))
            self.fieldcont[l].setText("%s %i: "%(
                translations["pokemonegggroup"], i+1))
            l = "egggroup_"+str(i)
            self.fieldcont[l] = QComboBox(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x+50, y, 100, 20))
            self.fieldcont[l].addItems(translations["pokemonegggroups"])
            QObject.connect(self.fieldcont[l],
                QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
            y += 25
        for i in range(itemcount):
            l = "abilitylabel_"+str(i)
            self.fieldcont[l] = QLabel(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x, y, 50, 20))
            self.fieldcont[l].setText("%s %i: "%(
                translations["pokemonability"], i+1))
            l = "ability_"+str(i)
            self.fieldcont[l] = QComboBox(self.generaltab)
            self.fieldcont[l].setGeometry(QRect(x+50, y, 100, 20))
            for t in self.abilitynames:
                self.fieldcont[l].addItem(t[1])
            QObject.connect(self.fieldcont[l],
                QtCore.SIGNAL("currentIndexChanged(int)"), self.changed)
            y += 25
        self.maintab = QWidget(self.tabcontainer)
        self.tabcontainer.addTab(self.maintab, translations["pokemontab_desc"])
        self.movetab = QWidget(self.tabcontainer)
        self.tmcont = []
        x = 10
        y = 5
        txt = "%s%%02i"%translations["pokemontm"]
        off = 0
        if pokeversion.gens[version[0]] == 4:
            tmmax = 92
        else:
            tmmax = 95
        for i in range(104):
            self.tmcont.append([QLabel(self.movetab), QCheckBox(self.movetab)])
            self.tmcont[i][0].setGeometry(QRect(x, y, 40, 20))
            if i == tmmax:
                txt = "%s%%02i"%translations["pokemonhm"]
                off = tmmax
            self.tmcont[i][0].setText(txt%(i-off+1))
            self.tmcont[i][1].setGeometry(QRect(x+38, y, 20, 20))
            y += 20
            if y > 260:
                y = 5
                x += 65
        self.tabcontainer.addTab(self.movetab, translations["pokemontab_moves"])
        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)
    def newPokemon(self):
        print("newPokemon() not implemented")
    def openPokemon(self, i):
        self.currentpoke = i
        self.opening = True
        personalnarc = narc.NARC(open(self.personalfname, "rb").read())
        self.natid.setText(translations["pokemon_natid"]+": "+str(i))
        version = config.project["versioninfo"]
        if pokeversion.gens[version[0]] == 4:
            personalfmt = "BBBBBBBBBBHHHBBBBBBBBBBxx"
            itemcount = 2
        elif pokeversion.gens[version[0]] == 5:
            personalfmt = "BBBBBBBBBBHHHHBBBBBBBBBBHHBBHHH"
            itemcount = 3
        sz = struct.calcsize(personalfmt)
        data = list(struct.unpack(personalfmt, personalnarc.gmif.files[i][:sz]))
        for stat in stats:
            self.fieldcont["stat_"+stat].setValue(data.pop(0))
        for i in range(2):
            self.fieldcont["type_"+str(i)].setCurrentIndex(data.pop(0))
        for field in ["catchrate", "baseexp"]:
            self.fieldcont["f_"+field].setValue(data.pop(0))
        evs = data.pop(0)
        for stat in stats:
            self.fieldcont["ev_"+stat].setValue(evs&3)
            evs >>= 2
        for i in range(itemcount):
            self.fieldcont["item_"+str(i)].setCurrentIndex(data.pop(0))
        for field in ["gender", "hatchcycle", "basehappy"]:
            self.fieldcont["f_"+field].setValue(data.pop(0))
        for field in ["exprate"]:
            self.fieldcont["f_"+field].setCurrentIndex(data.pop(0))
        for i in range(2):
            self.fieldcont["egggroup_"+str(i)].setCurrentIndex(data.pop(0))
        for i in range(itemcount):
            self.fieldcont["ability_"+str(i)].setCurrentIndex(data.pop(0))
        self.fieldcont["f_flee"].setValue(data.pop(0))
        for field in ["color"]:
            self.fieldcont["f_"+field].setCurrentIndex(data.pop(0))
        tmdata = struct.unpack("B"*13, 
            personalnarc.gmif.files[self.currentpoke][sz:sz+13])
        for i, d in enumerate(tmdata):
            for j in range(8):
                idx = i*8+j
                self.tmcont[idx][1].setChecked((tmdata[i]>>j)&1)
        del personalnarc
        self.opening = False
        self.dirty = False
        self.updateCurrentLabel()
    def savePokemon(self):
        print("savePokemon() not implemented")
    def quit(self):
        if not self.checkClean():
            return
        self.close()
    def checkClean(self, allowCancel=True):
        if self.dirty:
            if allowCancel:
                prompt = QMessageBox.question(self, "Close?", 
                    "This pokemon has been modified.\n"+
                        "Do you want to save this pokemon?",
                    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
                if prompt == QMessageBox.Cancel:
                    return False
            else:
                prompt = QMessageBox.question(self, "Close?", 
                    "This pokemon has been modified.\n"+
                        "Do you want to save this pokemon?",
                    QMessageBox.Yes, QMessageBox.No)
            if prompt == QMessageBox.Yes:
                if not self.savePokemon():
                    return False
        return True
    def changed(self, param1=None):
        if self.opening:
            return
        self.dirty = True
        self.updateCurrentLabel()
    def updateCurrentLabel(self):
        if self.dirty:
            dirt = " [modified]"
        else:
            dirt = ""
        self.setWindowTitle(wintitle%(self.pokemonnames[
            self.currentpoke][1]+dirt))
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
        return text
            
        
def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return
    EditPokemon(config.mw).show()