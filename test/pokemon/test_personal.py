
import unittest

from rawdb.pokemon.personal import Personal
from rawdb.util.io import BinaryIO


class TestPersonal(unittest.TestCase):
    def test_default(self):
        default = Personal()
        out = default.save().getvalue()
        new = Personal()
        new.load(BinaryIO(out))
        self.assertEqual(out, new.save().getvalue())

    def test_gen5(self):
        default = Personal(version=Personal.BLACK)
        out = default.save().getvalue()
        new = Personal(version=Personal.BLACK)
        new.load(BinaryIO(out))
        self.assertEqual(out, new.save().getvalue())
