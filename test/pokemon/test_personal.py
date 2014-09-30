
import unittest

from rawdb.pokemon.personal import Personal
from rawdb.util.io import BinaryIO


class TestPersonal(unittest.TestCase):
    def test_default(self):
        default = Personal()
        out = default.save().getvalue()
        print(len(out))
        new = Personal()
        new.load(BinaryIO(out))
        self.assertEqual(out, new.save().getvalue())
