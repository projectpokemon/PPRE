
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
        self.container['a']['b'].set_value(11)
        self.assertEqual(self.container['a']['b'].get_value(), 11)
        self.assertEqual(self.parent.x.b, self.container['a']['b'].get_value())

    def test_bind_twice(self):
        Bind(self.container, 'a', self.parent, 'x')
        self.setUp()
        Bind(self.container, 'a', self.parent, 'x')

    def test_unbind(self):
        binding = Bind(self.container, 'a', self.parent, 'x')
        binding.unbind()
        self.container['a']['d']['e'].set_value(22)
        self.parent.x.b = 7
        self.parent.x.d.e = 4
        self.container['a']['b'].set_value(11)
        self.assertEqual(len(self.parent.x.__setattr__._calls), 1)
        self.assertEqual(len(self.container['a']['b'].set_value._calls), 1)
        self.assertEqual(self.parent.x.b, 7)
        self.assertEqual(self.parent.x.d.e, 4)
        self.assertEqual(self.container['a']['b'].get_value(), 11)
        self.assertEqual(self.container['a']['d']['e'].get_value(), 22)

    def test_rebind(self):
        other_parent = Parent()
        self.container.bind('a', self.parent, 'x')
        self.container.bind('a', other_parent, 'x')
        self.parent.x.b = 5
        other_parent.x.b = 9
        self.assertEqual(self.parent.x.b, 5)
        self.parent.x.b = 8
        self.assertEqual(self.parent.x.b, 8)
        self.assertEqual(other_parent.x.b, 9)
        self.container['a']['b'].set_value(11)
        self.assertEqual(self.parent.x.b, 8)
        self.assertEqual(other_parent.x.b, 11)

    def test_bind_another(self):
        other_parent = Parent()
        self.container.bind('a', self.parent, 'x')
        self.container.bind('a', other_parent, 'x', False)
        self.parent.x.b = 5
        other_parent.x.b = 9
        self.assertEqual(self.parent.x.b, 9)
        self.assertEqual(other_parent.x.b, 9)
        self.parent.x.b = 8
        self.assertEqual(self.parent.x.b, 8)
        self.assertEqual(other_parent.x.b, 8)
        self.assertEqual(self.container['a']['b'].get_value(), 8)
        self.container['a']['d']['e'].set_value(22)
        self.assertEqual(self.parent.x.d.e, 22)
        self.assertEqual(other_parent.x.d.e, 22)

        return
        # FIXME: parent.x seems to become same object
        self.container.unbind('a')
        other_parent.x.b = 8
        self.parent.x.b = 4
        self.assertEqual(self.parent.x.b, 4)
        self.assertEqual(other_parent.x.b, 8)
        self.assertEqual(self.container['a']['b'].get_value(), 8)
        self.container['a']['b'].set_value(11)
        self.assertEqual(self.parent.x.b, 4)
        self.assertEqual(other_parent.x.b, 8)
        self.assertEqual(self.container['a']['b'].get_value(), 11)

