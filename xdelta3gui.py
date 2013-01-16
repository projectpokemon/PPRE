#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

import config
from language import translations
import xdelta3

class version:
    major = 1
    minor = 0
    revision = 1

def xd3setter(s, o, v, meta):
    key = s+"_"+o+"_value"
    if key not in meta:
        return
    meta[s+"_"+o+"_value"].setText(v)
    
class MainWindow(QMainWindow):
    def __init__(self, app, parent=None):
        super(MainWindow, self).__init__(parent)
        self.app = app
        self.setupUi()
    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowTitle("PPRE xdelta3 GUI %i.%i.%i"%
            (version.major, version.minor, version.revision))
        self.app.setApplicationName("PPRE xdelta3 GUI")
        self.app.setApplicationVersion("%i.%i.%i"%
            (version.major, version.minor, version.revision))
        self.resize(360, 180)
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
        self.menutasks["openproject"] = QAction(self.menus["file"])
        self.menutasks["openproject"].setText(translations["menu_openproject"])
        self.menutasks["openproject"].setShortcut("CTRL+O")
        self.menus["file"].addAction(self.menutasks["openproject"])
        QObject.connect(self.menutasks["openproject"],
            QtCore.SIGNAL("triggered()"), self.openProject)
        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.widgetcontainer = QWidget(self)
        self.widgetcontainer.setObjectName("widgetcontainer")
        self.projectinfo = {}
        self.projectinfo["location_base_name"] = QPushButton(
            self.widgetcontainer)
        self.projectinfo["location_base_name"].setGeometry(
            QRect(30, 30, 150, 25))
        self.projectinfo["location_base_name"].setText(
            translations["config_location_base_name"]+":")
        QObject.connect(self.projectinfo["location_base_name"],
            QtCore.SIGNAL("pressed()"), self.openBase)
        self.projectinfo["location_base_value"] = QLineEdit(
            self.widgetcontainer)
        self.projectinfo["location_base_value"].setGeometry(
            QRect(180, 30, 150, 25))
        self.projectinfo["project_output_name"] = QPushButton(
            self.widgetcontainer)
        self.projectinfo["project_output_name"].setGeometry(
            QRect(30, 60, 150, 25))
        self.projectinfo["project_output_name"].setText(
            translations["output_rom"]+":")
        self.projectinfo["project_output_value"] = QLineEdit(
            self.widgetcontainer)
        self.projectinfo["project_output_value"].setGeometry(
            QRect(180, 60, 150, 25))
        QObject.connect(self.projectinfo["project_output_name"],
            QtCore.SIGNAL("pressed()"), self.openOutput)
        self.projectinfo["patch_name"] = QPushButton(
            self.widgetcontainer)
        self.projectinfo["patch_name"].setGeometry(
            QRect(30, 90, 150, 25))
        self.projectinfo["patch_name"].setText(
            translations["patch_name"]+":")
        self.projectinfo["patch_value"] = QLineEdit(
            self.widgetcontainer)
        self.projectinfo["patch_value"].setGeometry(
            QRect(180, 90, 150, 25))
        QObject.connect(self.projectinfo["patch_name"],
            QtCore.SIGNAL("pressed()"), self.openPatch)
        self.projectinfo["apply_patch"] = QPushButton(
            self.widgetcontainer)
        self.projectinfo["apply_patch"].setGeometry(
            QRect(30, 120, 300, 25))
        self.projectinfo["apply_patch"].setText(
            translations["apply_patch"]+":")
        QObject.connect(self.projectinfo["apply_patch"],
            QtCore.SIGNAL("pressed()"), self.applyPatch)
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
        config.load(open(projFile, "r"), xd3setter, self.projectinfo)
        return
    def openBase(self):
        ndsFile = str(QFileDialog.getOpenFileName(None, "Open NDS ROM", 
            filter="NDS Files (*.nds);;All Files (*.*)"))
        if not ndsFile:
            return
        self.projectinfo["location_base_value"].setText(ndsFile)
    def openOutput(self):
        ndsFile = str(QFileDialog.getSaveFileName(None, "Open NDS ROM", 
            filter="NDS Files (*.nds);;All Files (*.*)"))
        if not ndsFile:
            return
        self.projectinfo["project_output_value"].setText(ndsFile)
    def openPatch(self):
        patchFile = QFileDialog.getOpenFileName(None, "Open Patch File", 
            filter="xdelta3 Patch Files (*.xdelta3);;All Files (*.*)")
        if not patchFile:
            return
        self.projectinfo["patch_value"].setText(patchFile)
    def applyPatch(self):
        inrom = str(self.projectinfo["location_base_value"].text())
        outrom = str(self.projectinfo["project_output_value"].text())
        patchFile = str(self.projectinfo["patch_value"].text())
        if not os.path.exists(inrom):
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_nooriginalrom"])
            return
        if not os.path.exists(patchFile):
            QMessageBox.critical(None, translations["error_noromloaded_title"], 
                translations["error_nopatch"])
            return
        xdelta3.applyPatch(patchFile, inrom, outrom)
        

app = QApplication(sys.argv)
mw = MainWindow(app)
mw.show()
app.exec_()