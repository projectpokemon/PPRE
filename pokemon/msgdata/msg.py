
import codecs
import os
import re

from atomic import AtomicStruct
from generic.archive import Archive
from generic.editable import XEditable as Editable
from pokemon import game
from util.io import BinaryIO


table = {}
rtable = {}

TEXT_KEY4_INIT = 0x91BD3  # Gen IV encryption initializer
TEXT_KEY4_STEP = 0x493D


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


def decompress(string, incr=15):
    """Decompress a character list

    Parameters
    ----------
    string : list
        List of char codes starting with 0xF100
    incr : int
        Width to increment by when moving. 15 for DPPt. 16 for BW

    Returns
    -------
    string : list
        The decompressed string
    """
    if string.pop(0) != 0xF100:
        raise ValueError('Invalid compression character')
    newstring = []
    container = 0
    bit = 0
    while string:
        container |= string.pop(0) << bit
        bit += incr
        while bit >= 9:
            bit -= 9
            char = container & 0x1FF
            if char == 0x1FF:
                newstring.append(0xFFFF)
            else:
                newstring.append(char)
            container >>= 9
    return newstring


class TableEntry(Editable):
    def define(self, version=game.Version(4, 0)):
        self.uint32('offset')
        self.uint32('charcount')
        if version > game.GEN_IV:
            with self.replace('charcount'):
                self.uint16('charcount')
                self.uint16('flags')


class Text(Archive, Editable):
    extension = '.txt'

    def define(self, version=game.Version(4, 0)):
        self.version = version
        if version in game.GEN_IV:
            self.uint16('num')
            self.uint16('seed')
            load_table()
        else:
            self.uint16('numblocks')
            self.uint16('num')
            self.uint32('filesize')
            self.uint32('null')

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        AtomicStruct.load(self, reader)
        self.files = {}
        offsets = []
        sizes = []
        if self.version in game.GEN_IV:
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
                key = (TEXT_KEY4_INIT*(i+1)) & 0xFFFF
                for j in range(size):
                    string.append(reader.readUInt16() ^ key)
                    key = (key+TEXT_KEY4_STEP) & 0xFFFF
                if string[0] == 0xF100:
                    compressed = True
                    string = decompress(string)
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
        else:
            commented = False
            for i in xrange(self.numblocks):
                offsets.append(reader.readUInt32())
            block = Editable()
            block.uint32('size')
            block.array('entries', TableEntry(self.version).base_struct,
                        length=self.num)
            block.freeze()
            for i, block_offset in enumerate(offsets):
                reader.seek(block_offset)
                block.load(reader)
                for j, entry in enumerate(block.entries):
                    compressed = False
                    text = ''
                    reader.seek(block_offset+entry.offset)
                    encchars = [reader.readUInt16()
                                for k in xrange(entry.charcount)]
                    seed = key = encchars[-1] ^ 0xFFFF
                    string = []  # decrypted chars
                    while encchars:
                        char = encchars.pop() ^ key
                        key = ((key >> 3) | (key << 13)) & 0xFFFF
                        string.insert(0, char)
                    if string[0] == 0xF100:
                        compressed = True
                        string = decompress(string, 16)
                    while string:
                        char = string.pop(0)
                        if char == 0xFFFF:
                            break
                        elif char == 0xFFFE:
                            text += '\\n'
                        elif char < 20 or char > 0xF000:
                            text += '\\x{0:04X}'.format(char)
                        elif char == 0xF000:
                            kind = string.pop(0)
                            count = string.pop(0)
                            if kind == 0xbe00 and not count:
                                text += '\\f'
                            elif kind == 0xbe01 and not count:
                                text += '\\r'
                            else:
                                text += 'VAR('
                                args = [kind]
                                args += string[:count]
                                string = string[count:]
                                text += ', '.join(map(str, args))
                                text += ')'
                        else:
                            text += unichr(char)
                    name = '{0}_{1:05}'.format(i, j)
                    c = 65
                    for k in xrange(16):
                        if (entry.flags >> k) & 0x1:
                            name += ord(c+k)
                    if compressed:
                        name += 'c'
                    name += '[{0:04X}]'.format(seed)
                    self.files[name] = text
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

    def save(self, writer=None):
        writer = BinaryIO()  # FIXME
        blocks = {}
        num = 0
        for name in self.files:
            match = re.match(
                '^(?P<block>[0-9]+c?)_'
                '(?P<idx>[0-9]{1,5})'
                '(?P<flags>[A-O]+c)?'
                '(:\\[(?P<key>[0-9A-F]{1,4})\\])?$', name)
            if not match:
                raise ValueError('{0} is not a valid identifier+options'
                                 .format(name))
            block_name = match.group('block')
            if block_name not in blocks:
                blocks[block_name] = {}
            idx = int(match.group('idx'))
            num = max(idx, num)
            flags = match.group('flags')
            try:
                key = int(match.group('key'), 16)
            except:
                key = 0
            blocks[block_name][idx] = (flags, key, self.files[name])
        if self.version in game.GEN_IV:
            if set(blocks.keys()) | {'0c', '0'} != {'0c', '0'}:
                raise ValueError('Gen IV cannot have any blocks other than'
                                 ' 0 (and 0c). Got: {0}'.format(blocks.keys()))
            blocks.pop('0c', None)  # TODO: handle comment blocks
            self.numblocks = 1
        else:
            self.numblocks = len(blocks)
        # base_offset = self.size()
        # if self.version > game.GEN_IV:
        #    base_offset += 4*self.numblocks
        # base_offset += TableEntry.instance(self.version).size()*self.numblocks
        self.num = num+1
        start = writer.tell()
        writer = AtomicStruct.save(self, writer)
        text_writer = BinaryIO()
        text_offs = writer.tell()+8*self.num
        prev_text_pos = 0
        for i, block_name in enumerate(blocks):
            # if self.version > game.GEN_IV:
            #     text_offs += 4*self.numblocks+text_writer.tell()-prev_text_pos
            #     prev_text_pos = text_writer.tell()
            for j in xrange(self.num):
                try:
                    flags, key, text = blocks[block_name][j]
                except KeyError:
                    flags = key = None
                    text = ''
                string = []
                cidx = 0
                while cidx < len(text):
                    char = text[cidx]
                    cidx += 1
                    if char == '\\':
                        char = text[cidx]
                        cidx += 1
                        if char == 'x':
                            n = int(text[cidx:cidx+4], 16)
                            cidx += 4
                        elif char == 'n':
                            n = 0xE000
                        elif char == 'r':
                            n = 0x25BC
                        elif char == 'f':
                            n = 0x25BD
                        elif char == 'u':
                            n = rtable['\\u'+text[cidx:cidx+4]]
                            cidx += 4
                        else:
                            n = 1
                        string.append(n)
                    elif text[:3] == 'VAR':
                        pass
                    else:
                        string.append(rtable[char])
                if flags and 'c' in flags:
                    raise NotImplementedError('Compression not yet Impld')
                string.append(0xFFFF)
                size = len(string)
                text_writer.writeAlign(4)
                state = (((self.seed*0x2FD) & 0xFFFF)*(j+1)) & 0xFFFF
                key = state | state << 16
                writer.writeUInt32(key ^ (text_offs+text_writer.tell()))
                writer.writeUInt32(key ^ size)
                key = (TEXT_KEY4_INIT*(j+1)) & 0xFFFF
                for char in string:
                    text_writer.writeUInt16(char ^ key)
                    key = (key+TEXT_KEY4_STEP) & 0xFFFF
            # TODO: comments
            writer.write(text_writer.getvalue())
        return writer
