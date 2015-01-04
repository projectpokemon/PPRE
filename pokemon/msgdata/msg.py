
import codecs
import os

from atomic import AtomicStruct
from generic.archive import Archive
from generic.editable import XEditable as Editable
from pokemon import game
from util.io import BinaryIO


table = {}
rtable = {}


def load_table():
    global table, rtable

    if table:
        return
    fname = 'Table.tbl'
    max_levels = 6
    while not os.path.exists(fname):
        max_levels -= 1
        if not max_levels:
            raise IOError('Could not find Table.tbl. Please place it in'
                          ' the PPRE directory')
        fname = os.path.join('../', fname)
    with codecs.open(fname, encoding='utf-16') as handle:
        for line in handle:
            key, value = line.strip('\r\n').encode('unicode_escape')\
                .split('=', 1)
            key = int(key, 16)
            table[key] = value
            rtable[value] = key


class Text(Archive, Editable):
    extension = '.txt'

    def define(self, version=game.Version(4, 0)):
        self.version = version
        self.uint16('num')
        self.uint16('seed')
        load_table()

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        AtomicStruct.load(self, reader)
        self.files = {}
        offsets = []
        sizes = []
        commented = (self.seed & 0x1FF) == 0x1FF
        for i in xrange(1, self.num+1):
            state = (((self.seed*0x2FD) & 0xFFFF)*i) & 0xFFFF
            key = state | state << 16
            offsets.append(reader.readUInt32() ^ key)
            sizes.append(reader.readUInt32() ^ key)
        if commented:
            state = (((self.seed*0x2FD) & 0xFFFF)*i) & 0xFFFF
            key = state | state << 16
            comment_ofs = reader.readUInt32() ^ key
            term = reader.readUInt32() ^ key
            if term != 0xFFFF:
                raise ValueError('Expected 0xFFFF comment ofs terminator.'
                                 ' Got {0:#x}'.format(term))
        for i in xrange(self.num):
            compressed = False
            reader.seek(offsets[i])
            size = sizes[i]
            string = []
            key = (0x91BD3*(i+1)) & 0xFFFF
            for j in range(size):
                string.append(reader.readUInt16() ^ key)
                key = (key+0x493D) & 0xFFFF
            if string[0] == 0xF100:
                compressed = True
                string.pop(0)
                newstring = []
                container = 0
                bit = 0
                while string:
                    container |= string.pop(0) << bit
                    bit += 15
                    while bit >= 9:
                        bit -= 9
                        char = container & 0x1FF
                        if char == 0x1FF:
                            newstring.append(0xFFFF)
                        else:
                            newstring.append(char)
                        container >>= 9
                string = newstring
            text = ''
            while string:
                char = string.pop(0)
                if char == 0xFFFF:
                    break
                elif char == 0xE000:
                    text += '\\n'
                elif char == 0x25bc:
                    text += '\\r'
                elif char == 0x25bd:
                    text += '\\f'
                else:
                    try:
                        text += table[char]
                    except KeyError:
                        text += '\\u{0:04x}'.format(char)
                name = '0_{0:05}'.format(i)
                if compressed:
                    name += 'c'
                self.files[name] = text
            else:
                raise RuntimeError('Did not have a terminating character')
        if commented:
            reader.seek(comment_ofs)
            num = reader.readUInt16()
            for i in xrange(num):
                commentid = reader.readUInt16()
                text = ''
                while True:
                    char = reader.readUInt16()
                    if char == 0xFFFF:
                        break
                    text += unichr(char)
                    name = '0c_{0:05}'.format(commentid)
                    self.files[name] = text
        return self
