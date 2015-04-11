
import json
import os

from compileengine import Decompiler, Variable, ExpressionBlock

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
    _fields = ('name', 'args', 'returns', )

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
        rets = []
        for idx, size in enumerate(self.args):
            if size == 'var':
                arg = decompiler.get_var(decompiler.read_value(2))
            elif size == 'flag':
                arg = decompiler.get_flag(decompiler.read_value(2))
            else:
                arg = decompiler.read_value(size)
                bin_arg = bin(arg)[2:-3]
                if bin_arg.count('0')*2 > bin_arg.count('1')*3 or\
                        bin_arg.count('1') > bin_arg.count('0')*3:
                    arg = hex(arg)
            if idx in self.returns:
                rets.append(arg)
            else:
                args.append(arg)
        if rets:
            if len(rets) == 1:
                rets = rets[0]
            return [decompiler.assign(rets, decompiler.func(
                self.name, *args, level=0))]
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
        if 'returns' not in data:
            data['returns'] = []
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
    _fields = Command._fields+('value', )

    def decompile_args(self, decompiler):
        if self.value is not False:
            self.value = True
        return [decompiler.end(self.value)]


class JumpCommand(Command):
    def decompile_args(self, decompiler):
        offset = decompiler.handle.readInt32()
        ofs2 = decompiler.tell()+offset
        if offset > 0:
            decompiler.seek(decompiler.tell()+offset)
        # return [decompiler.func(self.name, offset, ofs2)]
        return []


class SetConditionCommand(Command):
    def decompile_args(self, decompiler):
        exprs = Command.decompile_args(self, decompiler)
        args = exprs[0].args  # super().get_args
        decompiler.cond_state = decompiler.statement('<=>', *args)
        # return exprs
        return []


class ConditionalJumpCommand(Command):
    def decompile_args(self, decompiler):
        oper = decompiler.handle.readUInt8()  # FIXME: Handle this...
        offset = decompiler.handle.readInt32()
        restore = decompiler.tell()
        offset += restore
        decompiler.seek(offset)
        block = decompiler.branch_duplicate()
        block.start = offset
        # block.level = decompiler.level+1
        block.parse()
        decompiler.seek(restore)
        condition_expr = decompiler.condition(decompiler.cond_state)
        if len(condition_expr.conditional.args) == 1:
            if not oper:
                condition_expr.conditional = decompiler.func(
                    'not ', condition_expr.conditional.args[0],
                    level=0, namespace='')
        else:
            if oper == 0:
                condition_expr.conditional.operator = '<'
            elif oper == 1:
                condition_expr.conditional.operator = '=='
            elif oper == 2:
                condition_expr.conditional.operator = '>'
            elif oper == 4:
                condition_expr.conditional.operator = '>='
            elif oper == 5:
                condition_expr.conditional.operator = '!='
            else:
                raise NotImplementedError('Unknown operator: (<= ?)')
        return [condition_expr, block]


class MovementCommand(Command):
    def decompile_args(self, decompiler):
        target = decompiler.handle.readUInt16()
        offset = decompiler.handle.readInt32()
        restore = decompiler.tell()
        offset += restore
        decompiler.seek(offset)
        block = decompiler.branch_movement()
        block.start = offset
        # block.level = decompiler.level+1
        block.parse()
        block.lines.pop()  # 0xfe
        decompiler.seek(restore)
        return [decompiler.context(decompiler.func('move', target, level=0),
                                   'movement'), block]


class MessageCommand(Command):
    def decompile_args(self, decompiler):
        exprs = Command.decompile_args(self, decompiler)
        args = exprs[0].args  # super().get_args
        try:
            text_id = int(args[0])
        except:
            text_id = int(args[0], 0)
        try:
            text_str = decompiler.text[text_id]
        except IndexError:
            return exprs
        exprs[0].args = args+('text="{0}"'.format(
            text_str.encode('string_escape')), )
        return exprs


class ScriptDecompiler(Decompiler):
    def __init__(self, handle, script_container):
        Decompiler.__init__(self, handle)
        self.container = script_container
        self.commands = script_container.commands
        self.cond_state = None

    @property
    def text(self):
        if self.container.text is None:
            return []
        return self.container.text

    def parse_next(self):
        here = self.tell()
        cmd = self.read_value(2)
        if cmd is None:
            return [self.end()]
        if cmd > 750:
            return [self.unknown(cmd, 2)]
        command = self.commands.get(cmd, None)
        if command is not None:
            return command.decompile_args(self)
        return [self.unknown(cmd & 0xFF, 1), self.unknown(cmd >> 8, 1)]

    def branch_duplicate(self):
        dup = self.__class__(self.handle, self.container)
        dup.start = self.start
        return dup

    def branch_movement(self):
        dup = MovementDecompiler(self.handle, self.commands['movements'])
        dup.start = self.start
        return dup

    def get_var(self, id):
        var = Variable(id)
        var.name = 'var_{0:x}'.format(id)
        var.persist = True
        return var

    def get_flag(self, id):
        var = Variable(id)
        var.name = 'flag_{0:x}'.format(id)
        var.persist = True
        return var


class MovementDecompiler(Decompiler):
    def __init__(self, handle, movements):
        Decompiler.__init__(self, handle)
        self.movements = movements

    def parse_next(self):
        cmd = self.read_value(2)
        # if cmd is None:
        #     return [self.end()]
        if cmd == 0xFE:
            return [self.end()]
        command = self.movements.get(cmd)
        if command is None:
            command = 'mov_{0}'.format(cmd)
        return [self.func(command, namespace='movement.')]


class Script(object):
    """Pokemon Script handler

    JSON Commands are loaded (and overwritten) in this order:
    $PPRE_DIR/data/commands/base.json
    $PPRE_DIR/data/commands/base_custom.json (optional)
    $PPRE_DIR/data/commands/$GAME_COMMAND_FILES[0], etc.
    $GAME_DIR/commands.json (optional)

    Attributes
    ----------
    scripts : list of ScriptDecompiler
        Decompiled scripts
    commands : dict
        Command map

    Parameters
    ----------
    load(reader)
        Loads a single script file in and parses its scripts
    """
    def __init__(self, game):
        self.offsets = []
        self.scripts = []
        self.commands = {'movements': {}}
        self.text = None
        self.game = game
        self.load_commands(os.path.join(os.path.dirname(__file__), '..', '..',
                                        'data', 'commands', 'base.json'))
        try:
            self.load_commands(os.path.join(os.path.dirname(__file__), '..',
                                            '..', 'data', 'commands',
                                            'base_custom.json'))
        except IOError:
            pass
        for command_file in game.commands_files:
            self.load_commands(os.path.join(os.path.dirname(__file__), '..',
                                            '..', 'data', 'commands',
                                            command_file))
        try:
            self.load_commands(os.path.join(game.files.directory,
                                            'commands.json'))
        except IOError:
            pass

    def load(self, reader):
        self.offsets = []
        self.scripts = []
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
                script = ScriptDecompiler(reader, self)
                script.parse()
                script.header_lines.append('def script_{num}(engine):'
                                           .format(num=scrnum))
                self.scripts.append(script)

    def load_commands(self, fname):
        """Load commands from JSON file

        Parameters
        ----------
        fname : string
            Filename of JSON file
        """
        with open(fname) as handle:
            commands = json.load(handle)
        movements = commands.pop('movements', {})
        for cmd, command in movements.items():
            cmd = int(cmd, 0)
            self.commands['movements'][cmd] = command
        for cmd, data in commands.items():
            cmd = int(cmd, 0)
            self.commands[cmd] = Command.from_dict(cmd, data)

    def load_text(self, text):
        """Load a text archive to be associated with these scripts
        """
        self.text = text
