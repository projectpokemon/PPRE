

class ZCurve(object):
    def __init__(self):
        self.data = {}  # Sparse (x, y)=>val
        self.pos = 0

    def to_2d(self, ofs=0):
        x = 0
        y = 0
        shift = 0
        pos = self.pos+ofs
        while pos:
            x |= (pos & 0x1) << shift
            pos >>= 1
            y |= (pos & 0x1) << shift
            pos >>= 1
            shift += 1
        return (x, y)

    def append(self, val):
        self.data[self.to_2d()] = val
        self.pos += 1

    @property
    def height(self):
        w, h = self.to_2d(-1)
        return h+1

    @property
    def width(self):
        w, h = self.to_2d(-1)
        return w+1

    def __iter__(self):
        # Assume w, h are max
        for y in range(self.height):
            for x in range(self.width):
                yield self.data[(x, y)]


class ZCurveSkip(ZCurve):
    def __init__(self):
        super(ZCurveSkip, self).__init__()
        self.skip = True

    def append(self, val):
        if not self.skip:
            super(ZCurveSkip, self).append(val)
        self.skip = not self.skip


class ZCurveDouble(ZCurve):
    def append(self, val):
        super(ZCurveDouble, self).append(val)
        super(ZCurveDouble, self).append(val)
