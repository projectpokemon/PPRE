

from PyQt4 import QtCore, QtGui
QtWidgets = QtGui
from pressure.layout import Layout, LayoutChild

from ppre.gui.interface import Interface, QtLayoutChild


class EditInterface(Interface):
    def __init__(self, parent, *args, **kwargs):
        self.widget = None
        self.build_widget(parent, *args, **kwargs)
        print(parent.session, parent, self.widget)
        super(EditInterface, self).__init__(parent.session, parent,
                                            self.widget)
        print(self.session, self.parent, self.widget)

    def build_widget(self, parent, text, *args, **kwargs):
        widget = QtWidgets.QLineEdit(parent.widget)
        label = QtWidgets.QLabel(parent.widget)
        widget.setText(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(120, 0, 150, 20))
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        width = label.fontMetrics().boundingRect(text).width()
        label.setGeometry(QtCore.QRect(0, 0, width, 20))
        # label.setBuddy(widget)
        self.widget = widget
        self.label = label
        parent.layout.add_children(QtLayoutChild(self.label),
                                   QtLayoutChild(self.widget))


class NumberInterface(Interface):
    pass

