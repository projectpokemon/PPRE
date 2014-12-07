"""PyQt Graphical User Interface for PPRE

"""

import functools

from PyQt4 import QtCore, QtGui
QtWidgets = QtGui
from pressure.layout import Layout, LayoutChild

from ppre.interface import BaseInterface
from util import AttrDict

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


def q_simplify(value):
    if isinstance(value, QtCore.QString):
        return str(value)
    return value


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
        self._width = geometry.width()
        self._height = geometry.height()
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

    def updateGeometry(self):
        self.widget.setGeometry(self.x, self.y, self.width, self.height)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.updateGeometry()

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.updateGeometry()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self.updateGeometry()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.updateGeometry()


class Interface(BaseInterface):
    """Graphical User Interface"""
    def __init__(self, session, parent=None, widget=None):
        super(Interface, self).__init__(session)
        session_bind(session)
        self.parent = parent
        self.children = []
        if widget is None:
            self.widget = QtWidgets.QMainWindow(parent.widget if parent
                                                else None)
        else:
            self.widget = widget
        self._value = None
        self.blocking = False
        self.hiding = False
        try:
            QtCore.QObject.connect(self.widget,
                                   QtCore.SIGNAL('textEdited(const QString&)'),
                                   lambda value: self.set_value(str(value)))
        except:
            pass
        if self.parent is not None:
            self.parent.children.append(self)
            self.parent.fire('child:add', self)

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
    def shortcut(char, ctrl=False, shift=False, alt=False, meta=False):
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

    @staticmethod
    def connect(widget, signal_str, callback):
        QtCore.QObject.connect(widget, QtCore.SIGNAL(signal_str), callback)

    def connect_event(self, widget, signal_str, event, **event_map):
        """Emits an event on a Qt signal_str.

        Parameters
        ----------
        widget : QWidget
            Widget to connect to
        signal_str : str
            QString to listen on. This must take type parameters
        event : str
            Event name to emit
        event_map : **kwargs
            Map of argument types to attribute names. value=0, child=1, etc.
            To make data.value = arg[0] and data.child = arg[1]
        """
        def callback(*args):
            data = AttrDict()
            for key, value in event_map.items():
                data[key] = q_simplify(args[value])
            self.fire(event, data)
        self.connect(widget, signal_str, callback)

    def get_value(self):
        try:
            return str(self.widget.text())
        except:
            return None

    def set_value(self, value):
        if value == self._value:
            return
        print('value', self._value, value)
        self._value = value
        try:
            self.widget.setValue(value)
        except:
            try:
                self.widget.setText(value)
            except:
                pass
    value = property(lambda self: self.get_value(),
                     lambda self, new_value: self.set_value(new_value))

    def focus(self, interface):
        interface.on_focus()

    def on_focus(self):
        self.widget.setFocus()

    def menu(self, text):
        menu = QtWidgets.QMenu(self.menubar)
        menu.setTitle(text)
        self.menubar.addAction(menu.menuAction())
        menu_if = Interface(self.session, self, menu)
        return menu_if

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

    def multigroup(self, text, min=None, max=None):
        return MultiGroupInterface(self, text, min=min, max=max)

    def edit(self, text, soft_rows=None):
        return EditInterface(self, text)
    text = edit

    def number(self, text, min=None, max=None, step=None):
        return NumberInterface(self, text, min=min, max=max, step=step)

    def select(self, text, values):
        widget = QtWidgets.QComboBox(self.widget)
        label = QtWidgets.QLabel(self.widget)
        self.layout.add_children(QtLayoutChild(widget), QtLayoutChild(label))
        try:
            values.items
        except:
            widget.addItems([str(value) for value in values])
        else:
            for idx, value in values.items():
                widget.insertItem(idx, value)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(120, 0, 120, 20))
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        label.setGeometry(QtCore.QRect(0, 0, 110, 20))
        inf = Interface(self.session, self, widget)
        inf.connect_event(widget, 'currentIndexChanged(int)',
                          'changed', value=0)
        self.connect(widget, 'currentIndexChanged(int)',
                     lambda value: inf.set_value(value))
        return inf

    @attach_interface
    def message(self, text):
        # TODO: Better geometry guesses
        widget = QtWidgets.QLabel(self.widget)
        widget.setText(text)
        widget.setGeometry(QtCore.QRect(0, 0, 300, 20+20*text.count('\n')))
        return widget

    def boolean(self, text):
        widget = QtWidgets.QCheckBox(self.widget)
        self.layout.add_children(QtLayoutChild(widget))
        widget.setText(text)
        widget.setChecked(True)
        widget.setGeometry(QtCore.QRect(120, 0, 150, 20))
        return BooleanInterface(self.session, self, widget)

    def file(self, text, types=None, directory=False, new=False):
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
        return FileInterface(types, directory, new, self.session, self, widget)

    def prompt(self, text, block=True, hide=False):
        widget = QtWidgets.QDialog(self.widget)
        # widget.setModal(True)
        self.addWidget(widget)
        # widget.setTitle(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(0, 0, 0, 0))
        group_if = PromptInterface(self.session, self, widget)
        group_if.layout.padding_vertical = 50
        group_if.layout.padding_horizontal = 20
        action_buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, widget)
        action_buttons.setGeometry(0, 0, 300, 20)
        group_if.connect(action_buttons, 'accepted()', widget.accept)
        group_if.connect(action_buttons, 'rejected()', widget.reject)
        group_if.connect_event(widget, 'accepted()', '_okay')
        group_if.connect_event(widget, 'rejected()', '_cancel')
        group_if.connect_event(action_buttons, 'clicked(QAbstractButton*)',
                               'done')
        group_if.layout.add_children(QtLayoutChild(action_buttons))

        @group_if.on('cancel')
        def cancel(evt):
            if not evt.data:
                evt.cancel()
                widget.reject()

        @group_if.on('_cancel')
        def cancel(evt):
            group_if.fire('cancel', True)

        @group_if.on('okay')
        def okay(evt):
            if not evt.data:
                evt.cancel()
                widget.accept()

        @group_if.on('_okay')
        def okay(evt):
            group_if.fire('okay', True)

        group_if.blocking = block
        group_if.hiding = hide

        return group_if

    def title(self, text, color=None):
        self.widget.setWindowTitle(text)
        if color is not None:
            try:
                color = int(color[1:7], 16)
            except:
                pass
            red = (color >> 16) & 0xFF
            green = (color >> 8) & 0xFF
            blue = color & 0xFF
            bands = []
            for shift in range(16, -1, -8):
                tmp = (color >> shift) & 0xFF
                bands.append(str(tmp + ((190-tmp)/1.5)))
            color = 'rgb({0})'.format(','.join(bands))
            self.widget.setAutoFillBackground(False)
            self.widget.setStyleSheet("""
            QMainWindow {{ background-color: {color}; }}
            """.format(color=color))

    def icon(self, filename):
        icon = QtWidgets.QIcon()
        icon.addPixmap(QtWidgets.QPixmap(filename), icon.Normal, icon.Off)
        self.widget.setWindowIcon(icon)

    def show(self):
        if self.hiding:
            return
        try:
            self._layout
        except:
            pass
        else:
            state = hash(tuple(self.layout.children))
            print(self, self.layout.children)
            if state != self.layout.hash:
                self.layout.hash = state
            w, h = self.layout.optimize()
            print(self, w, h)
            self.widget.setGeometry(self.widget.x(), self.widget.y(), w, h)
        try:
            if self.blocking:
                self.widget.exec_()
            else:
                self.widget.show()
        except:
            pass

    def destroy(self):
        self.widget.close()

    def update(self):
        if self.parent:
            self.parent.update()
        self.show()

from ppre.gui.components import *
