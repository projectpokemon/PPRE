
from compileengine import Decompiler, Variable


class Register(object):
    SLOT_LR = 14
    SLOT_PC = 15

    def __init__(self, slot):
        self.slot = slot

    def __str__(self):
        if self.slot == self.SLOT_LR:
            return 'engine.lr'
        elif self.slot == self.SLOT_PC:
            return 'engine.pc'
        return 'engine.r{0}'.format(self.slot)

    def __eq__(self, other):
        return self.slot == other.slot


class ARM(Decompiler):
    """ARM 9 decompiler

    """
    variables = []
    registers = {}

    @staticmethod
    def get_reg(data, high=False):
        if high:
            data += 8
        return Register(data)

    @staticmethod
    def get_regs(data):
        regs = []
        for i in range(16):
            if data & (1 << i):
                regs.append(Register(i))
        return regs

    def get_var(self, reg, left=False):
        try:
            if left:
                raise KeyError
            var = self.registers[reg.slot]
        except KeyError:
            var = Variable(reg)
            self.variables.append(var)
            self.registers[reg.slot] = var
        if not left:
            var.refcount += 1
        return var

    @staticmethod
    def sign(value, bits):
        opp = 1 << bits
        if value & (opp >> 1):
            value -= opp
        return value

    def parse_next(self):
        cmd = self.read_value(4)
        return [self.unknown(cmd, 4)]

    def parse(self):
        """Read expression until return

        """
        parsed = self.prepare()
        while True:
            if not parsed:
                parsed = self.parse_next()
            try:
                expr = parsed.pop(0)
            except IndexError:
                # previous parse returned an empty list, request next
                continue
            self.lines.append(expr)
            if expr.is_return():
                break
        var_name = Variable.name_generator()
        for variable in self.variables:
            variable.name = var_name.next()
        return self.lines
