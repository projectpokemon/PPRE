from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from language import translations

def addAction(menu, name, action):
    a = QAction(menu)
    a.setText("menu_"+name)
    menu.addAction(a)
