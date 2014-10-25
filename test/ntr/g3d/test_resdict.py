
import unittest

from rawdb.ntr.g3d.resdict import G3DResDict, Node
from rawdb.util.io import BinaryIO


class TestG3DResDict(unittest.TestCase):
    def test_default(self):
        default = G3DResDict()
        default.data.append('\x00'*4)
        default.names.append('testing')
        default.nodes.append(Node(1, 2, 3, 4))
        out = default.save().getvalue()
        new = G3DResDict()
        new.load(BinaryIO(out))
        self.assertEqual(default.data, new.data)
        self.assertEqual(default.sizeunit, new.sizeunit)
        self.assertEqual(default.names, new.names)
        self.assertEqual(default.nodes, new.nodes)
