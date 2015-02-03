
from pokemon import game
from util.io import BinaryIO

MAX_ARGS = 8


class Method(object):
    def __init__(self, name=None):
        self.name = name
        self.forms = []
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
        while offset & 0xFFFF != 0xFD13 and offset:
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
