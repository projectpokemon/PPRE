
from PyQt4 import QtCore, QtGui
QtWidgets = QtGui

from ppre.gui.interface import Interface


class FileInterface(Interface):
    def __init__(self, types, is_directory, session, parent=None, widget=None):
        super(FileInterface, self).__init__(session, parent, widget)
        self.filter = ';;'.join(types)
        self.is_directory = is_directory
        QtCore.QObject.connect(self.widget.button, QtCore.SIGNAL('clicked()'),
                               self.on_focus)

    def on_focus(self):
        if not self.is_directory:
            fname = QtWidgets.QFileDialog.getOpenFileName(
                None, self.widget.label.text(), filter=self.filter)
        if not fname:
            return
        self.widget.setText(fname)
