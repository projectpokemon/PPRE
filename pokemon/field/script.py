
from compileengine import Decompiler, Variable

from util.io import BinaryIO


class Command(object):
    def __init__(self, name, arg_sizes):
        self.name = name
        self.arg_sizes = arg_sizes

    def decompile_args(self, decompiler):
        args = []
        for size in self.arg_sizes:
            args.append(decompiler.read_value(size))
        return [decompiler.func(self.name, *args)]


class ScriptDecompiler(Decompiler):
    def __init__(self, handle, commands, level=0):
        Decompiler.__init__(self, handle, level)
        self.commands = commands

    def parse_next(self):
        cmd = self.read_value(2)
        if cmd is None:
            return [self.end()]
        elif cmd in (0x2, 0x1b):
            return [self.end()]
        if cmd > 750:
            return [self.unknown(cmd, 2)]
        command = self.commands.get(cmd, None)
        if command is not None:
            return command.decompile_args(self)
        return [self.unknown(cmd & 0xFF, 1), self.unknown(cmd >> 8, 1)]


class Script(object):
    def __init__(self, game):
        self.offsets = []
        self.scripts = []
        self.commands = {}

    def load(self, reader):
        reader = BinaryIO.reader(reader)
        start = reader.tell()

        try:
            offset = reader.readUInt32()
        except:
            # Empty File. No script contents
            return
        while offset:
            abs_offset = offset+reader.tell()
            current_pos = reader.tell()
            for offset in self.offsets:
                if current_pos > offset:
                    break
            self.offsets.append(abs_offset)
            try:
                offset = reader.readUInt32()
            except:
                # Exhaustive offset list: not a script
                return
            if offset & 0xFFFF == 0xFD13:
                break
        if not self.offsets:
            return

        for scrnum, offset in enumerate(self.offsets):
            with reader.seek(offset):
                script = ScriptDecompiler(reader, self.commands, 1)
                script.parse()
                script.lines.insert(0, 'def script_{num}:'.format(num=scrnum))
                self.scripts.append(script)
