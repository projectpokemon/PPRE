from struct import unpack
from collections import namedtuple
from util.io import BinaryIO


class LZ(object):
    def __init__(self, reader):
        handle = BinaryIO.reader(reader)
        start = handle.tell()
        LZHeader = namedtuple('LZHeader', 'flag size')
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


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "rb") as f:
        open(sys.argv[2], "wb").write(LZ(f.read()).data)
