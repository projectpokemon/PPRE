
import unittest

from rawdb.ntr.g3d.btx import TEX, TexInfo
from rawdb.util.io import BinaryIO


class TestTEX(unittest.TestCase):
    def test_default(self):
        default = TEX()
        out = default.save().getvalue()
        new = TEX()
        new.load(BinaryIO(out))
        self.assertEqual(default.texparams, new.texparams)

    def test_texinfo(self):
        default = TexInfo(None)
        out = default.save().getvalue()
        new = TexInfo(None)
        new.load(BinaryIO(out))
        self.assertEqual(out, new.save().getvalue())
