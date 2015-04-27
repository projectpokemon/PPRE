
from generic import Editable
from generic.collection import SizedCollection
from util import BinaryIO


class Evolution(Editable):
    def define(self):
        self.uint16('method')
        self.uint16('param')
        self.uint16('target')


class Evolutions(SizedCollection):
    def define(self):
        SizedCollection.define(self, Evolution().base_struct, length=7,
                               resizable=False)
