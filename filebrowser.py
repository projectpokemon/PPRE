#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import os

import config
from language import translate
from nds import narc

def getFullPath(location):
    return config.project["directory"]+"fs"+location

def cleanMagic(magic):
    tmp = ""
    for c in magic:
        d = ord(c)
        if d > 0x20:
            tmp += c
        else:
            tmp += "_"
    return tmp

class LocationItem(QTreeWidgetItem):
    def __init__(self, location, parent=None):
        super(LocationItem, self).__init__(parent)
        self.location = location
        fname = location.split("/")[-1]
        self.setText(0, fname)
    def expand(self, e):
        self.setExpanded(e)
    def getType(self):
        return "Location"
    def setTexttoType(self):
        t = self.getType()
        if t:
            self.setText(1, t)
        else:
            self.setText(1, "Unknown")

class DirectoryItem(LocationItem):
    def __init__(self, location, parent=None):
        super(DirectoryItem, self).__init__(location, parent)
        self.setText(0, self.text(0)+"/")
        self.loadedChildren = False
        self.setTexttoType()
    def expand(self, e):
        if not self.loadedChildren:
            d = getFullPath(self.location)+"/"
            for f in sorted(os.listdir(d)):
                if os.path.isdir(d+"/"+f):
                    self.addChild(DirectoryItem(self.location+"/"+f, self))
                else:
                    self.addChild(FileItem(self.location+"/"+f, self))
            self.loadedChildren = True
        self.setExpanded(e)
    def getType(self):
        return "Directory"
        
class FileItem(LocationItem):
    def __init__(self, location, parent=None):
        super(FileItem, self).__init__(location, parent)
        self.magic = None
        self.setTexttoType()
        self.setText(2, str(os.path.getsize(getFullPath(self.location))))
    def getType(self):
        if not self.magic:
            f = open(getFullPath(self.location), "rb")
            self.magic = cleanMagic(f.read(4))
            f.close()
            if self.magic == "NARC":
                self.__class__ = ArchiveItem
                self.reinit()
                return self.getType()
        return self.magic
        
class ArchiveItem(FileItem):
    def __init__(self, location, parent=None):
        super(ArchiveItem, self).__init__(location, parent)
        self.reinit()
    def reinit(self):
        self.loadedChildren = False
        self.narc = None
    def getType(self):
        return "NARChive"
    def expand(self, e):
        if not self.loadedChildren:
            self.narc = narc.NARC(open(getFullPath(self.location), "rb").read())
            for i, f in enumerate(self.narc.gmif.files):
                af = ArchiveFileItem(self.location, i, self)
                af.magic = cleanMagic(f[:4])
                af.setSize(len(f))
                af.setTexttoType()
                self.addChild(af)
            self.loadedChildren = True
                
class ArchiveFileItem(FileItem):
    def __init__(self, location, index, parent=None):
        super(ArchiveFileItem, self).__init__(location, parent)
        self.setText(0, str(index))
    def getType(self):
        return self.magic
    def setSize(self, size):
        self.setText(2, str(size))

class FileTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(FileTreeWidget, self).__init__(parent)
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setTitle("Actions")
        at = QAction(menu)
        at.setText("Print")
        menu.addAction(at)
        menu.exec_(event.pos())

class FileBrowser(QMainWindow):
    BROWSE = 0
    CHOOSENARC = 1
    CHOOSEFILE = 2
    CHOOSEMULTI = 3
    def __init__(self, kind=BROWSE, parent=None):
        super(FileBrowser, self).__init__(parent)
        self.cb = None
        self.setupUi()
        if kind == self.BROWSE:
            self.setWindowTitle("File Browser - PPRE")
        elif kind == self.CHOOSENARC:
            self.setWindowTitle("Choose NARC")
        elif kind == self.CHOOSEFILE:
            self.setWindowTitle("Choose File")
        elif kind == self.CHOOSEMULTI:
            self.setWindowTitle("Choose Files")
        self.expand("/")
    def setupUi(self):
        self.setObjectName("FileBrowser")
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.filetree = QTreeWidget(self.widgetcontainer)
        self.filetree.setContextMenuPolicy(Qt.CustomContextMenu)
        QObject.connect(self.filetree,
            QtCore.SIGNAL("customContextMenuRequested(const QPoint&)"), 
            self.onContextMenu)
        self.filetree.setGeometry(0, 20, 600, 360)
        self.filetree.clear()
        self.root = DirectoryItem("/", self.filetree)
        self.filetree.addTopLevelItem(self.root)
        self.filetree.setHeaderLabels(["Location", "Type", "Size"])
        self.filetree.setColumnWidth(0, 300)
        self.filetree.setAllColumnsShowFocus(True)
        QObject.connect(self.filetree,
            QtCore.SIGNAL("itemDoubleClicked(QTreeWidgetItem *, int)"),
            self.itemExpanded)
        #self.filetree.setExpandsOnDoubleClick(True)
        self.setCentralWidget(self.widgetcontainer)
        QMetaObject.connectSlotsByName(self)
    def onContextMenu(self, point):
        menu = QMenu(self)
        menu.setTitle("Actions")
        at = QAction(menu)
        at.setText("Do nothing yet")
        menu.addAction(at)
        menu.exec_(self.filetree.mapToGlobal(point))
    def setCallback(self, cb):
        self.cb = cb
    def goto(self, location):
        self.currentnarc = location
        self.expand(location)
    def itemExpanded(self, item, col=0):
        if not item:
            return
        exp = self.filetree.isItemExpanded(item)
        item.expand(not exp)
        self.filetree.setItemExpanded(item, exp)
    def expand(self, location):
        items = self.filetree.findItems(location, 
            Qt.MatchExactly | Qt.MatchRecursive)
        for i in items:
            self.itemExpanded(i)
        
def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return
    FileBrowser(FileBrowser.BROWSE, config.mw).show()
    
def chooseFile(cb, loc=None):
    fb = FileBrowser(FileBrowser.CHOOSEFILE, config.mw)
    fb.setCallback(cb)
    if loc:
        fb.goto(loc)
    fb.show()