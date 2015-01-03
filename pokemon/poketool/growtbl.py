
from generic.editable import XEditable as Editable


class GrowTbl(Editable):
    def __init__(self, reader=None):
        Editable.__init__(self)
        self.array('experience_requirement', self.uint32, length=101)
        self.freeze()
