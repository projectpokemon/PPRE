#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

from language import translate

def defaultWidget(name, size, parent):
    sb = EditWidget(EditWidget.SPINBOX, parent)
    if size == 'H':
        sb.setValues([0, 0xFFFF])
    else:
        sb.setValues([0, 0xFF])
    sb.setName(translate(name))
    return sb
    
class EditWidget(QWidget):
    NONE = 0
    SPINBOX = 1
    COMBOBOX = 2
    def __init__(self, kind=SPINBOX, parent=None):
        super(EditWidget, self).__init__(parent)
        self.kind = kind
        self.label = QLabel(self)
        self.label.setGeometry(QRect(0, 0, 80, 20))
        self.valuer = None
        if kind == EditWidget.SPINBOX:
            self.valuer = QSpinBox(self)
            self.setValue = self.valuer.setValue
            self.getValue = self.valuer.value
            self.setValues = self.setSpinBoxValues
        elif kind == EditWidget.COMBOBOX:
            self.valuer = QComboBox(self)
            self.setValue = self.valuer.setCurrentIndex
            self.getValue = self.valuer.currentIndex
            self.setValues = self.valuer.addItems
        if self.valuer:
            self.valuer.setGeometry(QRect(80, 0, 80, 20))
    def setName(self, name):
        self.label.setText(name)
    def setSpinBoxValues(self, values):
        self.valuer.setMinimum(min(values))
        self.valuer.setMaximum(max(values))
    def getGeometry(self):
        if not self.valuer:
            return (self.label.geometry().width(),
                self.label.geometry().height())
        return (self.label.geometry().width()+self.valuer.geometry().width(),
            max([self.label.geometry().height(), 
                self.valuer.geometry().height()]))

class EditDlg(QMainWindow):
    wintitle = "Editor"
    def __init__(self, parent=None):
        super(EditDlg, self).__init__(parent)
        self.dirty = False
        self.currentchoice = 0
        self.game = "Diamond"
        self.setupUi()
        self.addEditableTab("General", ["BB", ["field 1"], ["field 2"]], None)
    def setupUi(self):
        self.setObjectName("EditDlg")
        self.resize(600, 400)
        icon = QIcon()
        icon.addPixmap(QPixmap("PPRE.ico"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, 600, 20))
        self.menus = {}
        self.menus["file"] = QMenu(self.menubar)
        self.menus["file"].setTitle(translate("menu_file"))
        self.menutasks = {}
        self.menubar.addAction(self.menus["file"].menuAction())
        self.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.widgetcontainer = QWidget(self)
        self.chooser = QComboBox(self.widgetcontainer)
        self.chooser.setGeometry(QRect(50, 25, 200, 20))
        QObject.connect(self.chooser,
            QtCore.SIGNAL("currentIndexChanged(int)"), self.openChoice)
        self.tabcontainer = QTabWidget(self.widgetcontainer)
        self.tabcontainer.setGeometry(QRect(25, 50, 550, 300))
        self.tabs = []
        self.setCentralWidget(self.widgetcontainer)
        self.updateWindowTitle()
        QMetaObject.connectSlotsByName(self)
    def openChoice(self, i):
        self.currentchoice = i
        self.dirty = False
    def changed(self, param1=None):
        self.dirty = True
        self.updateWindowTitle()
    def updateWindowTitle(self):
        if self.dirty:
            dirt = " [modified]"
        else:
            dirt = ""
        self.setWindowTitle("%s%s - %s - PPRE"%(self.chooser.currentText(),
            dirt, self.wintitle))
    def addEditableTab(self, tabname, fmt, boundnarc, getwidget=defaultWidget):
        tab = QScrollArea(self.tabcontainer)
        fields = []
        y = 10
        ypadding = 0
        x = 5
        for i, f in enumerate(fmt[0]):
            w = getwidget(fmt[i+1][0], f, tab)
            width, height = w.getGeometry()
            w.setGeometry(QRect(x, y, width, height))
            fields.append(w)
            y += ypadding + height
        self.tabs.append([tab, fields])
        self.tabcontainer.addTab(tab, tabname)
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mw = EditDlg(None)
    mw.show()
    app.exec_()