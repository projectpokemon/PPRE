"""

>>> from rawdb.elements.atom import BaseAtom
>>> class MyAtom(BaseAtom):
...     def __init__(self):
...         super(MyAtom, self).__init__()
...         self.int8('field1')
...         self.uint8('field2')
...         self.uint16('field3')
...
>>> atom = MyAtom()
>>> entry = atom('\xff\xff\x02\x01')
>>> entry.field1
-1
>>> entry.field3
258
>>> entry.field3 = 100
>>> str(entry)
'\xff\xff\x64\x00'

"""

from atomic import AtomicInstance, ThinAtomicInstance, DictAtomicInstance
from base_atom import BaseAtom
from valence import ValenceFormatter

__all__ = ['AtomicInstance', 'ThinAtomicInstance', 'DictAtomicInstance',
           'BaseAtom', 'ValenceFormatter']
