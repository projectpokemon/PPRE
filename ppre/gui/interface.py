"""PyQt Graphical User Interface for PPRE

"""

import functools

from PyQt4 import QtCore, QtGui
QtWidgets = QtGui
from pressure.layout import Layout, LayoutChild

from ppre.interface import BaseInterface

# Widget interfaces deferred until bottom of file


def attach_interface(func):
    """Make a method that returns a widget return an Interface"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        return Interface(self.session, self, func(self, *args, **kwargs))
    return wrapper


def session_bind(session):
    """Attach an application to the session if no application yet exists"""
    try:
        session.app
    except AttributeError:
        session.app = QtGui.QApplication(session.argv)


class QtLayoutChild(LayoutChild):
    """Pressure Layout container for Qt"""
    def __init__(self, widget):
        self.widget = widget
        self.element = self
        geometry = self.widget.geometry()
        self.widget.setGeometry = self.setGeometryWrapper(
            self.widget.setGeometry)
        self._x = geometry.x()
        self._y = geometry.y()
        self.width = geometry.width()
        self.height = geometry.height()
        super(QtLayoutChild, self).__init__(widget, width=self.width,
                                            height=self.height)

    def setGeometryWrapper(self, setGeometry):
        """When geometry of an object is changed, update this child"""
        # TODO: Bubble
        # TODO: Attach to resizeEvent
        @functools.wraps(setGeometry)
        def setGeometryUpdate(x, y=None, width=None, height=None):
            if y is width is height is None:
                # Case: QRect
                y = x.y()
                width = x.width()
                height = x.height()
                x = x.x()
            if self.x != x:
                self.x = x
            if self.y != y:
                self.y = y
            if self.width != width:
                self.width = width
            if self.height != height:
                self.height = height
            setGeometry(x, y, width, height)
        return setGeometryUpdate

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.widget.setGeometry(value, self.y, self.width, self.height)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.widget.setGeometry(self.x, value, self.width, self.height)


class Interface(BaseInterface):
    """Graphical User Interface"""
    def __init__(self, session, parent=None, widget=None):
        super(Interface, self).__init__(session)
        session_bind(session)
        self.parent = parent
        if self.parent is not None:
            self.parent.children.append(self)
        self.children = []
        if widget is None:
            self.widget = QtWidgets.QMainWindow(parent.widget if parent
                                                else None)
        else:
            self.widget = widget
        self._value = None
        try:
            QtCore.QObject.connect(self.widget,
                                   QtCore.SIGNAL('textEdited(const QString&)'),
                                   lambda value: self.set_value(value))
        except:
            pass

    @property
    def menubar(self):
        try:
            return self._menubar
        except AttributeError:
            self._menubar = QtWidgets.QMenuBar(self.widget)
            self.widget.setMenuBar(self._menubar)
            self.addWidget(self._menubar)
            return self._menubar

    @property
    def layout(self):
        try:
            return self._layout
        except AttributeError:
            self._layout = Layout()
            self._layout.hash = 0
            return self._layout

    def addWidget(self, widget):
        widget.setParent(self.widget)
        self.layout.add_children(QtLayoutChild(widget))

    def new(self):
        return Interface(self.session)

    @staticmethod
    def shortcut(self, char, ctrl=False, shift=False, alt=False, meta=False):
        parts = []
        if ctrl:
            parts.append('CTRL')
        if shift:
            parts.append('SHIFT')
        if alt:
            parts.append('ALT')
        if meta:
            parts.append('META')
        parts.append(char)
        return '+'.join(parts)

    def get_value(self):
        try:
            return self.widget.text()
        except:
            return None

    def set_value(self, value):
        print('value', value)
        if value == self._value:
            return
        self._value = value
        try:
            self.widget.setText(str(value))
        except:
            pass
    value = property(lambda self: self.get_value(),
                     lambda self, new_value: self.set_value(new_value))

    def focus(self, interface):
        interface.on_focus()

    def on_focus(self):
        self.widget.setFocus()

    @attach_interface
    def menu(self, text):
        menu = QtWidgets.QMenu(self.menubar)
        menu.setTitle(text)
        self.menubar.addAction(menu.menuAction())
        return menu

    @attach_interface
    def action(self, text, callback, shortcut=None):
        action = QtWidgets.QAction(self.widget)
        action.setText(text)
        if shortcut is not None:
            action.setShortcut(shortcut)
        self.widget.addAction(action)
        QtCore.QObject.connect(action, QtCore.SIGNAL('triggered()'), callback)
        return action

    def group(self, text):
        widget = QtWidgets.QGroupBox(None)
        self.addWidget(widget)
        widget.setTitle(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(0, 0, 0, 0))
        group_if = Interface(self.session, self, widget)
        group_if.layout.padding_vertical = 50
        group_if.layout.padding_horizontal = 20
        return group_if

    @attach_interface
    def edit(self, text, soft_rows=None):
        widget = QtWidgets.QLineEdit(self.widget)
        label = QtWidgets.QLabel(self.widget)
        # self.addWidget(widget)
        # self.addWidget(label)
        self.layout.add_children(QtLayoutChild(widget), QtLayoutChild(label))
        widget.setText(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(100, 0, 150, 20))
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        label.setGeometry(QtCore.QRect(0, 0, 150, 20))
        return widget

    def file(self, text, types=None, directory=False):
        widget = QtWidgets.QLineEdit(self.widget)
        label = QtWidgets.QLabel(self.widget)
        button = QtWidgets.QPushButton(self.widget)
        self.layout.add_children(QtLayoutChild(widget), QtLayoutChild(label),
                                 QtLayoutChild(button))
        widget.setText(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(100, 0, 150, 20))
        widget.label = label
        widget.button = button
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        label.setGeometry(QtCore.QRect(0, 0, 130, 20))
        button.setText('Browse')
        button.setContentsMargins(0, 0, 0, 0)
        button.setGeometry(QtCore.QRect(250, 0, 60, 20))
        return FileInterface(types, directory, self.session, self, widget)

    def prompt(self, text):
        widget = QtWidgets.QDialog(self.widget)
        # widget.setModal(True)
        self.addWidget(widget)
        # widget.setTitle(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(0, 0, 0, 0))
        group_if = Interface(self.session, self, widget)
        group_if.layout.padding_vertical = 50
        group_if.layout.padding_horizontal = 20
        action_buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, widget)
        action_buttons.setGeometry(0, 0, 300, 20)
        QtCore.QObject.connect(action_buttons, QtCore.SIGNAL('accepted()'),
                               widget.accept)
        QtCore.QObject.connect(action_buttons, QtCore.SIGNAL('rejected()'),
                               widget.reject)
        group_if.layout.add_children(QtLayoutChild(action_buttons))

        def on_okay(callback):
            QtCore.QObject.connect(widget, QtCore.SIGNAL('accepted()'), callback)
        group_if.on_okay = on_okay

        def on_cancel(callback):
            QtCore.QObject.connect(widget, QtCore.SIGNAL('rejected()'), callback)
        group_if.on_cancel = on_cancel

        return group_if

    def title(self, text):
        self.widget.setWindowTitle(text)

    def icon(self, filename):
        icon = QtWidgets.QIcon()
        icon.addPixmap(QtWidgets.QPixmap(filename), icon.Normal, icon.Off)
        self.widget.setWindowIcon(icon)

    def show(self):
        try:
            self._layout
        except:
            pass
        else:
            state = hash(tuple(self.layout.children))
            if state != self.layout.hash:
                self.layout.hash = state
            w, h = self.layout.optimize()
            self.widget.setGeometry(self.widget.x(), self.widget.y(), w, h)
        try:
            self.widget.show()
        except:
            pass

    def destroy(self):
        # TODO
        pass

from ppre.gui.widgets import *
