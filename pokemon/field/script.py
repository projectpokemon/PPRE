
import json

from compileengine import Decompiler, Variable

from util.io import BinaryIO


class CommandMetaRegistry(type):
    """Tracks the creation of Command derived classes
    """
    command_classes = {}

    def __new__(cls, name, parents, attrs):
        new_cls = type.__new__(cls, name, parents, attrs)
        if name in CommandMetaRegistry.command_classes:
            raise NameError('{0} is already a command class'.format(name))
        CommandMetaRegistry.command_classes[name] = new_cls
        return new_cls


class Command(object):
    """General Command class

    Subclasses are recorded into the meta registry and can be created via
    `Command.from_dict({'class': 'DerivedCommand', ...})`.

    Attributes
    ----------
    name : string
        Name of the command function
    args : list
        List of arg sizes

    Methods
    -------
    decompile_args : list of exprs
    to_dict : dict
    """
    __metaclass__ = CommandMetaRegistry
    _fields = ('name', 'args', )

    def decompile_args(self, decompiler):
        """Generates decompiled command expressions by reading its arguments
        from the active decompiler

        Parameters
        ----------
        decompiler : ScriptDecompiler
            Active decompiler

        Returns
        -------
        exprs : list
            List of expressions generated. This is typically just one function.
        """
        args = []
        for size in self.args:
            args.append(decompiler.read_value(size))
        return [decompiler.func(self.name, *args)]

    @staticmethod
    def from_dict(cmd, data):
        """Generate a Command from a dictionary

        Parameters
        ----------
        cmd : int
            Command idx
        data : dict
            Dict to generate from

        Returns
        -------
        command : Command
        """
        class_name = data.pop('class', 'Command')
        cls = CommandMetaRegistry.command_classes[class_name]
        if 'name' not in data:
            data['name'] = 'cmd_{0}'.format(cmd)
        if 'args' not in data:
            data['args'] = []
        command = cls()
        for field in cls._fields:
            setattr(command, field, data.get(field))
        return command

    def to_dict(self):
        """Saves this command back to a json-serializable dict.

        This takes all attributes from `_fields` as well as the class
        name (if not the default Command class).
        """
        command_dict = {}
        for field in self._fields:
            command_dict[field] = getattr(self, field)
        if self.__class__.__name__ != 'Command':
            command_dict['class'] = self.__class__.__name__
        return command_dict


class EndCommand(Command):
    _fields = Command.fields+('value', )

    def decompile_args(self, decompiler):
        if self.value is not False:
            self.value = True
        return [self.decompiler.end()]


class ScriptDecompiler(Decompiler):
    def __init__(self, handle, commands, level=0):
        Decompiler.__init__(self, handle, level)
        self.commands = commands

    def parse_next(self):
        cmd = self.read_value(2)
        if cmd is None:
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
        self.game = game

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

    def load_commands(self, fname):
        """Load commands from JSON file

        Parameters
        ----------
        fname : string
            Filename of JSON file
        """
        for cmd, data in json.load(fname).items():
            self.commands[cmd] = Command.from_dict(cmd, data)
