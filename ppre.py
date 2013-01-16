#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

from compat import *
import config
from language import translations
import ndstool, xdelta3
import pokeversion

import edittext, editpokemon, editmoves

class version:
    major = 2
    minor = 2
    revision = 0

if "--help" in sys.argv or "-h" in sys.argv:
    print("""Project Pokemon ROM Editor 2 - 2012
Usage: %s [options]
Options:
 --load/-l project.pprj     Loads a project
 --new /-n ndsfile.nds      Creates a new project from a ROM
 --dlg /-d dialog           Starts a dialog
 
Dialogs:
 home                       Main Window
 texteditor                 Text Editor
 pokemoneditor              Pokemon Editor"""%(sys.argv[0]))
    exit()
    
class MainWindow(QMainWindow):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)
        self.parent = parent
        self.app = app
        self.projFile = None
        config.mw = self
        self.setupUi()
        self.dirty = False
        args = sys.argv[1:]
        while args:
            arg = args.pop(0)
            if arg in ["-l", "--load"]:
                self.openProjectOf(args.pop(0))
            elif arg in ["-n", "--new"]:
                self.newProjectOf(args.pop(0))
            elif arg in ["-d", "--dialog"]:
                arg = args.pop(0)
                if arg == "home":
                    pass
                elif arg == "texteditor":
                    edittext.create()
                elif arg == "pokemoneditor":
                    editpokemon.create()
            else:
                print("Unrecognized argument: %s"%arg)
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("PPRE %i.%i.%i"%
            (version.major, version.minor, version.revision))
        self.app.setApplicationName("PPRE")
        self.app.setApplicationVersion("%i.%i.%i"%
            (version.major, version.minor, version.revision))
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.app.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translations["menu_file"])
        self.menutasks = {}
        self.menutasks["newproject"] = QAction(self.menus["file"])
        self.menutasks["newproject"].setText(translations["menu_newproject"])
        self.menutasks["newproject"].setShortcut("CTRL+N")
        self.menus["file"].addAction(self.menutasks["newproject"])
        QObject.connect(self.menutasks["newproject"],
            QtCore.SIGNAL("triggered()"), self.newProject)
        self.menutasks["openproject"] = QAction(self.menus["file"])
        self.menutasks["openproject"].setText(translations["menu_openproject"])
        self.menutasks["openproject"].setShortcut("CTRL+O")
        self.menus["file"].addAction(self.menutasks["openproject"])
        QObject.connect(self.menutasks["openproject"],
            QtCore.SIGNAL("triggered()"), self.openProject)
        self.menutasks["saveproject"] = QAction(self.menus["file"])
        self.menutasks["saveproject"].setText(translations["menu_saveproject"])
        self.menutasks["saveproject"].setShortcut("CTRL+S")
        self.menus["file"].addAction(self.menutasks["saveproject"])
        QObject.connect(self.menutasks["saveproject"],
            QtCore.SIGNAL("triggered()"), self.saveProject)
        self.menutasks["saveprojectas"] = QAction(self.menus["file"])
        self.menutasks["saveprojectas"].setText(translations["menu_saveprojectas"])
        self.menutasks["saveprojectas"].setShortcut("CTRL+SHIFT+S")
        self.menus["file"].addAction(self.menutasks["saveprojectas"])
        QObject.connect(self.menutasks["saveprojectas"],
            QtCore.SIGNAL("triggered()"), self.saveProjectAs)
        self.menutasks["exportrom"] = QAction(self.menus["file"])
        self.menutasks["exportrom"].setText(translations["menu_exportrom"])
        self.menus["file"].addAction(self.menutasks["exportrom"])
        QObject.connect(self.menutasks["exportrom"],
            QtCore.SIGNAL("triggered()"), self.exportRom)
        self.menutasks["exportromas"] = QAction(self.menus["file"])
        self.menutasks["exportromas"].setText(translations["menu_exportromas"])
        self.menus["file"].addAction(self.menutasks["exportromas"])
        QObject.connect(self.menutasks["exportromas"],
            QtCore.SIGNAL("triggered()"), self.exportRomAs)
        self.menutasks["makepatch"] = QAction(self.menus["file"])
        self.menutasks["makepatch"].setText(translations["menu_makepatch"])
        self.menus["file"].addAction(self.menutasks["makepatch"])
        QObject.connect(self.menutasks["makepatch"],
            QtCore.SIGNAL("triggered()"), self.makePatch)
        self.menutasks["quit"] = QAction(self.menus["file"])
        self.menutasks["quit"].setText(translations["menu_quit"])
        self.menutasks["quit"].setShortcut("CTRL+Q")
        self.menus["file"].addAction(self.menutasks["quit"])
        QObject.connect(self.menutasks["quit"],
            QtCore.SIGNAL("triggered()"), self.quit)
        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.widgetcontainer.setObjectName("widgetcontainer")
        self.menus["edit"] = QMenu(self.menubar)
        self.menus["edit"].setTitle(translations["menu_edit"])
        self.menutasks["edittext"] = QAction(self.menus["edit"])
        self.menutasks["edittext"].setText(translations["menu_edittext"])
        self.menus["edit"].addAction(self.menutasks["edittext"])
        QObject.connect(self.menutasks["edittext"],
            QtCore.SIGNAL("triggered()"), edittext.create)
        self.menutasks["editpokemon"] = QAction(self.menus["edit"])
        self.menutasks["editpokemon"].setText(translations["menu_editpokemon"])
        self.menus["edit"].addAction(self.menutasks["editpokemon"])
        QObject.connect(self.menutasks["editpokemon"],
            QtCore.SIGNAL("triggered()"), editpokemon.create)
        self.menutasks["editmoves"] = QAction(self.menus["edit"])
        self.menutasks["editmoves"].setText(translations["menu_editmoves"])
        self.menus["edit"].addAction(self.menutasks["editmoves"])
        QObject.connect(self.menutasks["editmoves"],
            QtCore.SIGNAL("triggered()"), editmoves.create)
        self.menubar.addAction(self.menus["edit"].menuAction())
        self.projectinfo = {}
        i = 0
        for sect in config.sections:
            for opt in config.options[sect]:
                self.projectinfo[sect+"_"+opt+"_name"] = QLabel(
                    self.widgetcontainer)
                self.projectinfo[sect+"_"+opt+"_name"].setGeometry(
                    QRect(30, 30*(i+1), 150, 25))
                self.projectinfo[sect+"_"+opt+"_name"].setText(
                    translations["config_%s_name"%(sect+"_"+opt)]+":")
                self.projectinfo[sect+"_"+opt+"_value"] = QLineEdit(
                    self.widgetcontainer)
                self.projectinfo[sect+"_"+opt+"_value"].setGeometry(
                    QRect(180, 30*(i+1), 150, 25))
                i += 1
        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)
    def openProject(self):
        projFile = QFileDialog.getOpenFileName(None, "Open PPRE Project File", 
            filter="PPRE Project Files (*.pprj);;All Files (*.*)")
        if not projFile:
            return
        self.openProjectOf(projFile)
    def openProjectOf(self, projFile):
        self.projFile = projFile
        config.load(open(projFile, "r"), config.qtSetter, self.projectinfo)
        config.project = {"directory": 
            self.projectinfo["location_directory_value"].text()}
        config.project["versioninfo"] = pokeversion.get()
        return
    def newProject(self):
        ndsFile = str(QFileDialog.getOpenFileName(None, "Open NDS ROM", 
            filter="NDS Files (*.nds);;All Files (*.*)"))
        if not ndsFile:
            return
        self.newProjectOf(ndsFile)
    def newProjectOf(self, ndsFile):
        d, tail = os.path.split(os.path.abspath(ndsFile))
        name = os.path.splitext(tail)[0]
        d += "/"+name+"/"
        if os.path.exists(d):
            prompt = QMessageBox.question(None, "Overwrite directory?", 
                "%s already exists. Would you like this "%d.rstrip("/")+
                    "to be overwritten with the project directory?\n"+
                    "All contents will be deleted. This cannot be undone.",
                QMessageBox.Yes, QMessageBox.No)
            if prompt == QMessageBox.Yes:
                if os.path.isdir(d):
                    shutil.rmtree(d)
                else:
                    os.unlink(d)
            else:
                return
        os.makedirs(d)
        ndstool.dump(ndsFile, d)
        self.dirty = True
        prompt = QMessageBox.question(None, "Create backup?", 
            "Would you like to create a backup of this ROM in your "+
                "project directory?",
            QMessageBox.Yes, QMessageBox.No)
        if prompt == QMessageBox.Yes:
            shutil.copyfile(ndsFile, d+"base.nds")
        self.projectinfo["location_base_value"].setText(d+"base.nds")
        self.projectinfo["location_directory_value"].setText(d)
        self.projectinfo["project_name_value"].setText(name.title())
        self.projectinfo["project_output_value"].setText(d+"edit.nds")
        config.project = {"directory": 
            self.projectinfo["location_directory_value"].text()}
        config.project["versioninfo"] = pokeversion.get()
    def saveProject(self):
        if not self.projFile:
            self.saveProjectAs()
        else:
            self.saveProjectOf(self.projFile)
    def saveProjectAs(self):
        projFile = QFileDialog.getSaveFileName(None, "Save PPRE Project File", 
            filter="PPRE Project Files (*.pprj);;All Files (*.*)")
        if not projFile:
            return
        self.projFile = projFile
        self.saveProjectOf(projFile)
    def saveProjectOf(self, projFile):
        config.write(open(projFile, "w"), config.qtGetter, self.projectinfo)
        self.dirty = False
        return
    def exportRom(self):
        self.exportRomTo(self.projectinfo["project_output_value"].text())
    def exportRomAs(self):
        ndsFile = str(QFileDialog.getSaveFileName(None, "Open Save ROM", 
            filter="NDS Files (*.nds);;All Files (*.*)"))
        if not ndsFile:
            return
        exportRomTo(ndsFile)
    def exportRomTo(self, output):
        if not config.project:
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_noromloaded"])
            return
        ndstool.build(output, config.project["directory"])
        return
    def makePatch(self):
        if not config.project:
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_noromloaded"])
        inrom = str(self.projectinfo["location_base_value"].text())
        outrom = str(self.projectinfo["project_output_value"].text())
        if not os.path.exists(inrom):
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_nooriginalrom"])
            return
        if not os.path.exists(outrom):
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_nonewrom"])
            return
        patchFile = QFileDialog.getSaveFileName(None, "Save Patch File", 
            filter="xdelta3 Patch Files (*.xdelta3);;All Files (*.*)")
        if not patchFile:
            return
        xdelta3.makePatch(patchFile, inrom, outrom)
    def quit(self):
        if self.dirty:
            prompt = QMessageBox.question(None, "Close?", 
                "Your project has been modified.\n"+
                    "Do you want to save your project file?",
                QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
            if prompt == QMessageBox.Cancel:
                return
            if prompt == QMessageBox.Yes:
                self.saveProject()
        exit(0)
        

app = QApplication(sys.argv)
mw = MainWindow(app)
mw.show()
app.exec_()