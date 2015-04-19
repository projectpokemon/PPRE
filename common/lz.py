
import array
from struct import unpack, pack
from collections import namedtuple

from util.io import BinaryIO

COMPRESSION_LZ77 = 0x10
COMPRESSION_LZSS = 0x11


LZHeader = namedtuple('LZHeader', 'flag size')


class LZ(object):
    def __init__(self, reader):
        handle = BinaryIO.reader(reader)
        start = handle.tell()
        raw_header = unpack('I', handle.read(4))[0]
        self.header = LZHeader._make([raw_header&0xFF, raw_header>>8])
        if self.header.flag == 0x11:
            lz_ss = True
        elif self.header.flag == 0x10:
            lz_ss = False
        else:
            raise ValueError('Invalid compression flag: {0}'
                             .format(self.header.flag))
        out = []
        while len(out) < self.header.size:
            flag = unpack('B', handle.read(1))[0]
            for x in range(7, -1, -1):
                if len(out) >= self.header.size:
                    break
                if not (flag >> x) & 0x1:
                    r = handle.read(1)
                    out.append(r)
                    continue
                head, = unpack('>H', handle.read(2))
                if not lz_ss:
                    count = ((head >> 12) & 0xF) + 3
                    back = head & 0xFFF
                else:
                    ind = (head >> 12) & 0xF
                    if not ind:
                        tail = unpack('B', handle.read(1))[0]
                        count = (head >> 4) + 0x11
                        back = ((head & 0xF) << 8) | tail
                    elif ind == 1:
                        tail = unpack('>H', handle.read(2))[0]
                        count = (((head & 0xFFF) << 4) | (tail >> 12)) + 0x111
                        back = tail & 0xFFF
                    else:
                        count = ind + 1
                        back = head & 0xFFF
                cursz = len(out)
                for y in range(count):
                    out.append(out[cursz-back-1+y])
        self.data = "".join(out)
        handle.seek(start)
        handle.write(self.data)
        handle.seek(start)
        self.handle = handle

    @staticmethod
    def is_lz(data):
        return ord(data[0]) in (0x10, 0x11)


class LZCompress(object):
    """LZ77 Compression. Basic sliding window implementation
    """
    def __init__(self, reader, compression=COMPRESSION_LZ77):
        handle = BinaryIO.reader(reader)
        start = handle.tell()
        data = array.array('B', handle.read())
        self.header = LZHeader._make([compression, len(data)])
        handle.truncate(start)
        handle.seek(start)
        handle.write(pack('I', self.header.flag | (self.header.size << 8)))

        out = array.array('B')
        out.append(0)
        out.extend(data[:4])
        pos = 4
        endpos = len(data)
        search_start = 0
        max_len = 0x12
        control_bit = 4
        flag = 0
        flag_pos = 0
        while pos < endpos:
            best_pos = None
            best_len = 0
            for check in xrange(search_start, pos):
                for idx in xrange(0, min(max_len+1, pos-check, endpos-pos)):
                    if data[check+idx] != data[pos+idx]:
                        break
                if idx >= best_len:
                    best_len = idx
                    best_pos = check
                    if idx >= max_len:
                        break
            control_bit -= 1
            if best_len < 3:
                out.append(data[pos])
                pos += 1
            else:
                flag |= 1 << control_bit
                head = (best_len-3) << 0xC
                head |= pos-best_pos-1
                out.append(head >> 8)
                out.append(head & 0xFF)
                pos += best_len
            if control_bit <= 0:
                if pos >= 0x400:
                    search_start = pos-0x400
                control_bit = 8
                out[flag_pos] = flag
                flag_pos = len(out)
                flag = 0
                out.append(0)
        out[flag_pos] = flag
        handle.write(out.tostring())
        self.handle = handle


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as f:
        open(sys.argv[2], "wb").write(LZ(f.read()).data)
