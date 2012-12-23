#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

import config
from language import translations
import pokeversion
from nds import narc, txt

files = pokeversion.pokemonfiles 

wintitle = "%s - Pokemon Editor - PPRE"

class EditPokemon(QMainWindow):
    def __init__(self, parent=None):
        super(EditPokemon, self).__init__(parent)
        self.setupUi()
        self.dirty = False
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
        self.widgetcontainer.setObjectName("widgetcontainer")
        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)
    def newPokemon(self):
        print("newPokemon() not implemented")
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
                if not self.saveText():
                    return False
        return True
        
def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return
    EditPokemon(config.mw).show()