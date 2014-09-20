
import unittest

from rawdb.elements.atom.base_atom import BaseAtom
from rawdb.elements.atom.valence import *
from rawdb.elements.atom.valence import ValenceCopy, resolve_atomic


class ValenceTestCase(unittest.TestCase):
    def test_valence_copy(self):
        valent = ValenceFormatter('test', 'c')
        valent.some_attr = 'blah'
        copy = ValenceCopy(valent)
        copy.name = 'copy'

        self.assertEqual(valent.name, 'test')
        self.assertEqual(copy.name, 'copy')
        self.assertEqual(valent.some_attr, 'blah')
        self.assertEqual(copy.some_attr, 'blah')

    def test_atomic_resolution(self):
        atom = BaseAtom()
        """
        struct {
            uint16 a;
            struct {
                uint16 a;
                struct {
                    uint16 a;
                } c;
            } b;
        } atom;
        """
        a_1 = atom.uint16('a')
        atom.sub_push('b')
        a_2 = atom.uint16('a')
        atom.sub_push('c')
        a_3 = atom.uint16('a')
        atom.sub_pop()
        atom.sub_pop()

        data = '\x02\x00\x03\x00\x04\x00'
        atomic = atom(data)
        self.assertEqual(resolve_atomic(atomic, a_1), atomic)
        self.assertEqual(resolve_atomic(atomic, a_2), atomic.b)
        self.assertEqual(resolve_atomic(atomic.b, a_1), atomic)
        self.assertEqual(resolve_atomic(atomic.b, a_2), atomic.b)
        self.assertEqual(resolve_atomic(atomic.b, a_3), atomic.b.c)
        self.assertEqual(resolve_atomic(atomic.b.c, a_1), atomic)
        self.assertEqual(resolve_atomic(atomic.b.c, a_3), atomic.b.c)

        self.assertEqual(str(atomic), data)

    def test_atomic_resolution_on_arrays(self):
        atom = BaseAtom()
        """
        struct {
            uint16 a;
            struct {
                uint16 a;
                struct {
                    uint16 a;
                } c[a];
            } b;
        } atom;
        """
        a_1 = atom.uint16('a')
        atom.sub_push('b')
        a_2 = atom.uint16('a')
        atom.sub_push('c')
        a_3 = atom.uint16('a')
        c = atom.array(atom.sub_pop(), count=a_2)
        b = atom.sub_pop()

        data = '\x02\x00\x03\x00\x06\x00\x05\x00\x04\x00'
        atomic = atom(data)
        self.assertEqual(resolve_atomic(atomic, a_1), atomic)
        self.assertEqual(resolve_atomic(atomic.b.c[1], a_1), atomic)
        self.assertEqual(resolve_atomic(atomic.b.c[1], a_3), atomic.b.c)
        self.assertEqual(resolve_atomic(atomic, a_3), atomic.b.c)

    def test_valence_name(self):
        atom = BaseAtom()
        """
        struct {
            uint16 a;
            struct {
                uint16 a;
                struct {
                    uint16 a;
                } c;
            } b;
        } atom;
        """
        a_1 = atom.uint16('a')
        atom.sub_push('b')
        a_2 = atom.uint16('a')
        atom.sub_push('c')
        a_3 = atom.uint16('a')
        atom.sub_pop()
        atom.sub_pop()

        self.assertIn('b.c.a', repr(a_3))
