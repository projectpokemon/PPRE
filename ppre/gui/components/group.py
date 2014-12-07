
import functools

from PyQt4 import QtCore, QtGui
QtWidgets = QtGui
from pressure.layout import Layout, LayoutChild

from ppre.gui.interface import Interface, QtLayoutChild


class GroupInterface(Interface):
    def __init__(self, parent, *args, **kwargs):
        self.widget = None
        self.build_widget(parent, *args, **kwargs)
        super(GroupInterface, self).__init__(parent.session, parent,
                                             self.widget)
        self.layout.padding_horizontal = 50
        self.layout.padding_vertical = 20

    def build_widget(self, parent, text, *args, **kwargs):
        widget = QtWidgets.QGroupBox(parent.widget)
        parent.addWidget(widget)
        widget.setTitle(text)
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setGeometry(QtCore.QRect(0, 0, 0, 0))
        self.widget = widget

    @staticmethod
    def make_label(parent, text):
        label = QtWidgets.QLabel(parent.widget)
        label.setText(text)
        label.setContentsMargins(0, 0, 0, 0)
        width = label.fontMetrics().boundingRect(text).width()
        label.setGeometry(QtCore.QRect(0, 0, width, 20))
        return label


class MultiGroupInterface(GroupInterface):
    def __init__(self, text, *args, **kwargs):
        super(MultiGroupInterface, self).__init__(text, *args, **kwargs)
        if kwargs.get('max'):
            self.layout.ratio = float(kwargs.get('max'))
        self.subgroups = []
        self.clone_builders = []
        self._value_sign = 0

    def build_widget(self, parent, text, *args, **kwargs):
        super(MultiGroupInterface, self).build_widget(parent, text,
                                                      *args, **kwargs)
        self.container = self.widget  # Objects go into here
        # Template fills up here (self.widget)
        super(MultiGroupInterface, self).build_widget(parent, text,
                                                      *args, **kwargs)

    def x__getattribute__(self, name):
        attr = super(MultiGroupInterface, self).__getattribute__(name)
        if not hasattr(attr, '__call__'):
            return attr
        if '_' in name:
            # Currently holds true for all non-interface returners
            return attr

        @functools.wraps(attr)
        def wrapper(*args, **kwargs):
            ret = attr(*args, **kwargs)
            if isinstance(ret, Interface):
                builder = (name, args, kwargs)
                if builder not in self.clone_builders:
                    self.clone_builders.append(builder)
            return ret
        return wrapper

    def add_clone(self, value):
        widget = self.widget
        self.widget = self.container
        group = super(MultiGroupInterface, self).group('entry')
        for name, args, kwargs in self.clone_builders:
            getattr(group, name)(*args, **kwargs)
        group.layout.ratio = self.layout.ratio
        group.show()
        self.widget = widget
        self.subgroups.append(group)

    def set_value(self, value):
        if len(value) == self._value_sign:
            return
        self._value_sign = len(value)
        print('MGI value', value)
        self._value = value
        for group in self.subgroups:
            group.destroy()
        for subvalue in value:
            self.add_clone(subvalue)

    def show(self):
        print(self.layout.__dict__)
        widget = self.widget
        self.widget = self.container
        for group in self.subgroups:
            group.show()
        super(MultiGroupInterface, self).show()
        self.widget = widget
        self.widget.hide()
