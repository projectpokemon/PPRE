
from PyQt4 import QtCore, QtGui
QtWidgets = QtGui

from ppre.gui.interface import Interface


class FileInterface(Interface):
    def __init__(self, types, is_directory, new, session, parent=None,
                 widget=None):
        super(FileInterface, self).__init__(session, parent, widget)
        if types:
            self.filter = ';;'.join(types)
        else:
            self.filter = ''
        self.is_directory = is_directory
        self.new = new
        self.connect_event(widget, 'textEdited(const QString&)',
                           'changed', value=0)
        self.connect(self.widget.button, 'clicked()', self.on_focus)

    def on_focus(self):
        if self.is_directory:
            fname = QtWidgets.QFileDialog.getExistingDirectory(
                None, self.widget.label.text())
        else:
            if self.new:
                fname = QtWidgets.QFileDialog.getSaveFileName(
                    None, self.widget.label.text(), filter=self.filter)
            else:
                fname = QtWidgets.QFileDialog.getOpenFileName(
                    None, self.widget.label.text(), filter=self.filter)
        if not fname:
            self.fire('cancel')
        else:
            self.set_value(fname)
            self.fire('okay')
        self.fire('done')
