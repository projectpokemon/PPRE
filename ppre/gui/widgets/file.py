
from PyQt4 import QtCore, QtGui
QtWidgets = QtGui

from ppre.gui.interface import Interface


class FileInterface(Interface):
    def __init__(self, types, is_directory, session, parent=None, widget=None):
        super(FileInterface, self).__init__(session, parent, widget)
        if types:
            self.filter = ';;'.join(types)
        else:
            self.filter = ''
        self.is_directory = is_directory
        QtCore.QObject.connect(self.widget.button, QtCore.SIGNAL('clicked()'),
                               self.on_focus)

    def on_focus(self):
        if self.is_directory:
            fname = QtWidgets.QFileDialog.getExistingDirectory(
                None, self.widget.label.text())
        else:
            fname = QtWidgets.QFileDialog.getOpenFileName(
                None, self.widget.label.text(), filter=self.filter)
        print(fname, self.set_value)
        if not fname:
            return
        self.set_value(fname)
