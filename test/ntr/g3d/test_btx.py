
import unittest

from rawdb.ntr.g3d.btx import BTX, TEX, TexInfo, TexParam
from rawdb.util.io import BinaryIO


class TestBTX(unittest.TestCase):
    def test_default(self):
        default = BTX()
        out = default.save().getvalue()
        new = BTX()
        new.load(BinaryIO(out))
        self.assertEqual(out, new.save().getvalue())


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

    def test_texparams(self):
        default = TEX()
        default.texdict.num = 1
        default.texparams = [TexParam(0, 16, 16, 3, 0)]
        default.texdict.names.append('test1')
        out = default.save().getvalue()
        new = TEX()
        new.load(BinaryIO(out))
        self.assertEqual(default.texparams, new.texparams)
