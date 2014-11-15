
import unittest

from ppre.ui.bind import Bind
from ppre.ui.base_ui import BaseUserInterface


class UI(object):
    def __init__(self):
        self._value = 5

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value


class ModelA(object):
    def __init__(self):
        self.b = 7
        self.c = 8
        self.d = ModelD()
        self.ui = UI()
        self.get_value = self.ui.get_value
        self.set_value = self.ui.set_value


class ModelD(object):
    def __init__(self):
        self.e = 9
        self.ui = UI()
        self.get_value = self.ui.get_value
        self.set_value = self.ui.set_value


class Parent(object):
    def __init__(self):
        self.x = ModelA()


class TestBind(unittest.TestCase):
    def setUp(self):
        self.container = BaseUserInterface(UI(), 'container', None, None)
        a = BaseUserInterface(UI(), 'a', None, self.container)
        BaseUserInterface(UI(), 'b', None, a)
        BaseUserInterface(UI(), 'c', None, a)
        d = BaseUserInterface(UI(), 'd', None, a)
        BaseUserInterface(UI(), 'e', None, d)
        self.parent = Parent()

    def test_bind(self):
        Bind(self.container, 'a', self.parent, 'x')
        self.parent.x.b = 8
        self.assertEqual(self.parent.x.b, 8)
        self.assertEqual(self.parent.x.b, self.container['a']['b'].get_value())

    def test_bind_twice(self):
        Bind(self.container, 'a', self.parent, 'x')
        self.setUp()
        Bind(self.container, 'a', self.parent, 'x')

    def test_rebind(self):
        other_parent = Parent()
        Bind(self.container, 'a', self.parent, 'x')
        Bind(self.container, 'a', other_parent, 'x')
        other_parent.x.b = 9
        self.assertEqual(self.parent.x.b, 7)
        self.parent.x.b = 8
        self.assertEqual(self.parent.x.b, 8)
        self.assertEqual(other_parent.x.b, 9)
