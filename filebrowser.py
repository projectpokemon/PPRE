#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui

import config

def create():
    if not config.project:
        QMessageBox.critical(None, translations["error_noromloaded_title"], 
            translations["error_noromloaded"])
        return