
from pokemon import game
from util.io import BinaryIO

MAX_ARGS = 16
MIN_REFS = 25
MIN_CONFIDENCE = .75


class Method(object):
    def __init__(self, name=None):
        self.name = name
        self.forms = {}
        self.args = None
        self.known = False
        self.minbytes = 0
        self.maxbytes = 16

    def argsize(self):
        if self.args is None:
            return self.minbytes
        if not self.args:
            return 0
        return sum(self.args)

    def add_form(self, *args, **kwargs):
        weight = kwargs.get('weight')
        if self.minbytes <= sum(args) <= self.maxbytes:
            if args in self.forms:
                self.forms[args] += weight
            else:
                self.forms[args] = weight

    def resolve(self):
        ref_count = sum(self.forms.values())
        if ref_count > MIN_REFS:
            for args, count in self.forms.iteritems():
                if self.minbytes <= sum(args) <= self.maxbytes:
                    if count/ref_count > MIN_CONFIDENCE:
                        self.args = args
                        break
            self.forms = {}

    def __repr__(self):
        if self.known:
            return '<Method "{0}" argsize={1}>'.format(self.name, self.argsize())
        return '<Method "{0}">'.format(self.name)


class Script(object):
    def __init__(self, *args, **kwargs):
        reader = kwargs.pop('reader', None)
        self.define(*args, **kwargs)
        if reader is not None:
            self.load(reader)

    def define(self, version=game.Version(4, 0)):
        self.version = version
        self.methods = {}

    def learn(self, reader, methods):
        reader = BinaryIO.reader(reader)
        start = reader.tell()
        self._offsets = []
        self._regions = {}

        def mark(size, advance=False):
            if advance:
                self._regions[reader.tell()] = size
            else:
                self._regions[reader.tell()-size] = size

        def check(size=None):
            reg = reader.tell()
            if size is None:
                return self._regions.get(reg, 0) is 0
            elif not size:
                return True
            elif reg in self._regions:
                return self._regions[reg] == size
            for i in xrange(1, 16):
                try:
                    if self._regions[reg-i] > i:
                        return False
                    break
                except:
                    pass
            for i in xrange(1, size):
                if reg+i in self._regions:
                    return False
            return True

        try:
            offset = reader.readUInt32()
        except:
            return
        while offset:
            # print(reader.tell(), self._regions)
            if not check():
                break
            abs_offset = offset+reader.tell()
            self._offsets.append(abs_offset)
            mark(4)
            with reader.seek(abs_offset):
                mark(2, True)
            try:
                offset = reader.readUInt32()
            except:
                return
            if offset & 0xFFFF == 0xFD13:
                with reader.seek(reader.tell()-2):
                    mark(2)
                break
        if not self._offsets:
            return

        with reader.seek(reader.tell()):
            while True:
                try:
                    reader.readUInt8()
                except:
                    break
            if self._offsets[0] > reader.tell():
                return
            mark(255, True)

        def parse():
            if not check(2):
                return
            cmd = reader.readUInt16()
            mark(2)
            if not cmd:
                return
            if cmd in (0x16, 0x1A):
                offset = reader.readInt32()
                mark(4)
                with reader.seek(offset+reader.tell()):
                    parse()
                parse()
                return
            elif cmd in (0x1C, 0x1D) and 0:
                arg = reader.readUInt8()
                mark(1)
                offset = reader.readInt32()
                mark(4)
                with reader.seek(offset+reader.tell()):
                    parse()
                parse()
                return
            elif cmd in (0x5E,):
                arg = reader.readUInt16()
                mark(2)
                offset = reader.readInt32()
                mark(4)
                with reader.seek(offset+reader.tell()):
                    arg = 0
                    while arg != 0xFE:
                        if not check(2):
                            raise Exception('Movement')
                        arg = reader.readUInt16()
                        mark(2)
                return
            if cmd not in methods:
                method = Method(cmd)
                methods[cmd] = method
            else:
                method = methods[cmd]
            if method.known:
                argsize = method.argsize()
                if not check(argsize):
                    print(cmd, argsize, reader.tell(), self._regions)
                    raise Exception
                    return
                reader.read(argsize)
                if argsize:
                    mark(argsize)
                parse()
                return
            minbytes = 0
            while True:
                if check(1):
                    if not check(2):
                        minbytes += 1
                        method.known = True
                        if minbytes == 1:
                            method.args = [1]
                        else:
                            method.maxbytes = method.minbytes = minbytes
                        reader.readUInt8()
                        mark(1)
                        parse()
                        return
                    else:
                        arg = reader.readUInt16()
                        if arg & 0xC000 and not arg & 0x0F00:
                            minbytes += 2
                            method.minbytes = max(minbytes, method.minbytes)
                        else:
                            break
                else:
                    method.known = True
                    if minbytes == 0:
                        method.args = []
                    else:
                        method.maxbytes = method.minbytes = minbytes
                    parse()
                    return

        for offset in self._offsets:
            with reader.seek(offset):
                # mark(2, True)
                parse()

        spaces = []
        space_start = None
        reader.seek(start)
        for i in xrange(start, max(self._regions)):
            if check(1):
                if space_start is None:
                    space_start = i
                space_end = i
            else:
                if space_start is not None:
                    spaces.append([space_start, space_end+1])
                space_start = None
            reader.readUInt8()

        def check_parse(size, affinity=1.0):
            print('Size', size)
            if not size:
                return 1*affinity
            if not check():
                return 1*affinity
            if size == 1:
                if check(1):
                    if reader.readUInt8():
                        return -1*affinity
            size -= 2
            if size < 0:
                return 0
            if not check(2):
                # If we started inside of a parameter of the last, seek forward
                with reader.seek(reader.tell()+1):
                    return check_parse(size-1, affinity)*affinity
            cmd = reader.readUInt16()
            print('Active', cmd)
            if not cmd:
                return 0
            if cmd > 0x500:
                return -2*affinity
            try:
                method = methods[cmd]
            except KeyError:
                method = Method(cmd)
                methods[cmd] = method
            if method.known:
                argsize = method.argsize()
                if size > argsize:
                    return -2*affinity
                reader.read(argsize)
                passed = 0
                with reader.seek(reader.tell()):
                    passed += check_parse(size-argsize, affinity)
                return passed*affinity
            elif method.minbytes:
                if size < method.minbytes:
                    return -2*affinity
            elif not size:
                method.add_form(weight=0.5)
                return 0.5*affinity
            passed = 0
            for k in xrange(method.minbytes, min(size+1, MAX_ARGS)):
                with reader.seek(reader.tell()):
                    print(k)
                    reader.read(size-k)
                    ret = check_parse(k, affinity/2.0)
                    method.add_form(*[1]*(size-k), weight=ret)
                    passed += ret*.5
            return passed/k*affinity

        for space in spaces:
            if space[1] - space[0] < 16:
                # print(self._regions)
                for i in xrange(space[0], space[1]):
                    for j in xrange(i, space[1]):
                        # print(j, i, space)
                        with reader.seek(j-2):
                            # print(reader.tell(), check(), check(2))
                            with reader.seek(reader.tell()):
                                print([reader.readUInt8() for k in xrange(space[1]-j+2)])
                            check_parse(space[1]-j+2)
