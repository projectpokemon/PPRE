
import unittest

from rawdb.elements.atom.base_atom import BaseAtom


class AtomsTestCase(unittest.TestCase):
    def test_subclass(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.uint16('a')
                self.uint16('b')
        data = '\x02\x00'*2
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.a, 2)
        self.assertEqual(atomic.b, 2)
        self.assertEqual(str(atomic), data)

    def test_subatom(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.sub_push('a')
                self.uint16('b')
                self.sub_pop()
        data = '\x02\x00'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(str(atomic), data)
        self.assertEqual(atomic.a.b, 2)

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.uint16('a')
                self.uint16('b')
                self.sub_push('c')
                self.uint16('d')
                self.sub_pop()
        data = '\x02\x00'*3
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.a, 2)
        self.assertEqual(atomic.b, 2)
        self.assertEqual(atomic.c.d, 2)
        self.assertEqual(str(atomic), data)

    def test_array(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.array(self.uint16('a'), count=4)
        data = '\x02\x00'*3+'\x03\x00'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(str(atomic), data)
        self.assertEqual(atomic.a[0], 2)
        self.assertEqual(atomic.a[3], 3)
        self.assertEqual(len(atomic.a), 4)

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.array(self.uint16('a'), terminator=0xFFFF)
        data = '\x02\x00'*3+'\xff\xff'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.a[0], 2)
        self.assertEqual(len(atomic.a), 3)
        self.assertEqual(str(atomic), data)

    def test_array_modification(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                a = self.uint16('a')
                self.array(self.uint16('b'), count=a)
        data = '\x02\x00\x02\x00\x02\x00'
        atom = Atom()
        atomic = atom(data)
        atomic.b.append(3)
        atomic.b.append(4)
        self.assertEqual(str(atomic),
                         '\x04\x00\x02\x00\x02\x00\x03\x00\x04\x00')

    def test_array_shells(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                a = self.uint16('a')
                self.array(self.uint16('b'), count=a*2)
        data = '\x01\x00\x02\x00\x02\x00'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.a, 1)
        self.assertEqual(len(atomic.b), 2)
        self.assertEqual(str(atomic), data)

    def test_array_subshells(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.sub_push('info')
                self.uint16('a')
                info = self.sub_pop()
                self.array(self.uint16('b'), count=info.a*2)
        data = '\x01\x00\x02\x00\x02\x00'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.info.a, 1)
        self.assertEqual(len(atomic.b), 2)
        self.assertEqual(str(atomic), data)

    def test_array_subshell_modification(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                self.sub_push('info')
                self.uint16('a')
                info = self.sub_pop()
                self.array(self.uint16('b'), count=info.a)
        data = '\x02\x00\x02\x00\x02\x00'
        atom = Atom()
        atomic = atom(data)
        atomic.b.append(3)
        atomic.b.append(4)
        self.assertEqual(str(atomic),
                         '\x04\x00\x02\x00\x02\x00\x03\x00\x04\x00')

    def test_data_shells(self):

        class Atom(BaseAtom):
            def __init__(self):
                super(Atom, self).__init__()
                a = self.uint16('a')
                self.data('b', count=a*2)
        data = '\x02\x00BEEF'
        atom = Atom()
        atomic = atom(data)
        self.assertEqual(atomic.a, 2)
        self.assertEqual(atomic.b, 'BEEF')
        self.assertEqual(str(atomic), data)
