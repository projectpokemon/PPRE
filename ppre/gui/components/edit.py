

from PyQt4 import QtCore, QtGui
QtWidgets = QtGui
from pressure.layout import Layout, LayoutChild

from ppre.gui.interface import Interface, QtLayoutChild


class EditInterface(Interface):
    def __init__(self, parent, *args, **kwargs):
        self.widget = None
        self.build_widget(parent, *args, **kwargs)
        super(EditInterface, self).__init__(parent.session, parent,
                                            self.widget)
        print(self.session, self.parent, self.widget)

    def build_widget(self, parent, text, *args, **kwargs):
        widget = QtWidgets.QLineEdit(parent.widget)
        widget.setText('')
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(120, 0, 150, 20))
        self.widget = widget
        self.label = self.make_label(parent, text)
        self.label.setBuddy(self.widget)
        parent.layout.add_children(QtLayoutChild(self.label),
                                   QtLayoutChild(self.widget))
        self.connect(widget, 'textEdited(const QString&)',
                     lambda value: self.set_value(str(value)))
        self.connect_event(widget, 'textEdited(const QString&)',
                           'changed', value=0)

    @staticmethod
    def make_label(parent, text):
        label = QtWidgets.QLabel(parent.widget)
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        width = label.fontMetrics().boundingRect(text).width()
        label.setGeometry(QtCore.QRect(0, 0, width, 20))
        return label


class NumberInterface(EditInterface):
    def build_widget(self, parent, text, min=None, max=None, step=None,
                     *args, **kwargs):
        widget = QtWidgets.QSpinBox(parent.widget)
        if min is None:
            widget.setValue(0)
        else:
            widget.setMinimum(min)
            widget.setValue(min)
        if max is not None:
            widget.setMaximum(max)
        if step is not None:
            widget.setSingleStep(step)
        width = widget.fontMetrics().boundingRect(
            '-MM'+str(widget.maximum())).width()+20
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(120, 0, width, 20))
        self.widget = widget
        self.label = self.make_label(parent, text)
        self.label.setBuddy(self.widget)
        parent.layout.add_children(QtLayoutChild(self.label),
                                   QtLayoutChild(self.widget))
        self.connect_event(widget, 'valueChanged(int)',
                           'changed', value=0)
        self.connect(widget, 'valueChanged(int)',
                     lambda value: self.set_value(value))
