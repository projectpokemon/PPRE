
from compileengine.assembler import Disassembler


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


class Thumb(Disassembler):
    stack = []

    @staticmethod
    def get_regs(data):
        regs = []
        for i in range(16):
            if data & (1 << i):
                regs.append(Register(i))
        return regs

    @staticmethod
    def get_reg(data, high=False):
        if high:
            data += 8
        return Register(data)

    @staticmethod
    def sign(value, bits):
        opp = 1 << bits
        if value & (opp >> 1):
            value -= opp
        return value

    def parse_next(self):
        cmd = self.read_value(2)
        if cmd & 0b1111100000000000 == 0b0001100000000000:
            # add/sub
            src = self.get_reg((cmd >> 3) & 0x7)
            dest = self.get_reg(cmd & 0x7)
            if cmd & 0x200:
                oper = '-'
            else:
                oper = '+'
            if cmd & 0x400:
                val = (cmd >> 6) & 7
            else:
                val = self.get_reg((cmd >> 6) & 0x7)
            return [self.assign(dest, self.statement(oper, src, val))]
            # TODO: cspr
        elif cmd & 0b1110000000000000 == 0b0010000000000000:
            # add/sub/cmp/mov immediate
            oper = (cmd >> 11) & 3
            src = self.get_reg((cmd >> 8) & 0x7)
            val = cmd & 0xFF
            if oper == 0:
                # mov
                return [self.assign(src, val)]
            elif oper == 1:
                # TODO: cmp
                pass
            elif oper == 2:
                oper = '+'
            elif oper == 3:
                oper = '-'
            return [self.assign(src, self.statement(oper, src, val))]
        elif cmd & 0b1111011000000000 == 0b1011010000000000:
            regs = self.get_regs(cmd & 0x7F)
            if cmd & 0x800:
                func = 'pop'
                if cmd & 0x100:
                    regs.append(Register(Register.SLOT_PC))
            else:
                func = 'push'
                if cmd & 0x100:
                    regs.append(Register(Register.SLOT_LR))
            return [self.build(func, *regs)]
        elif cmd & 0b1111100000000000 == 0b1110000000000000:
            # b
            self.seek(self.tell()+(cmd & 0x3FF))
            return []
        elif cmd & 0b1111000000000000 == 0b1111000000000000:
            # bl
            ofs = (cmd & 0x7FF) << 12
            ofs += (self.read_value(2) & 0x7FF) << 1
            ofs = self.sign(ofs, 23) + self.tell()
            return [self.build('bl', ofs)]
        elif cmd & 0b1111111100000000 == 0b0100011100000000:
            # bx
            reg = self.get_reg((cmd >> 3) & 0x7, cmd & 0x40)
            if reg.slot == Register.SLOT_LR:
                return [self.end()]
            return [self.build('bx', reg)]
        elif cmd & 0b1111100000000000 == 0b0100100000000000:
            # ldr dest [pc, #v]
            pass
        elif cmd & 0b1111001000000000 == 0b0101000000000000:
            # ldr/str Rd [Rb, Ro]
            if cmd & 0x400:
                size = 'byte'
            else:
                size = 'word'
            ofs = self.get_reg((cmd >> 6) & 7)
            base = self.get_reg((cmd >> 3) & 7)
            dest = self.get_reg(cmd & 7)
            if cmd & 0x800:
                func = 'get'  # ldr
                return [self.assign(dest, self.build(
                    'ram.get_{0}'.format(size), self.add(base, ofs), level=0))]
            else:
                func = 'set'  # str
                return [self.build('ram.set_{0}'.format(size),
                                   self.add(base, ofs), dest)]
        elif cmd & 0b1110000000000000 == 0b0110000000000000:
            # ldr/str Rd [Rb, #ofs]
            ofs = (cmd >> 6) & 0x1F
            base = self.get_reg((cmd >> 3) & 7)
            dest = self.get_reg(cmd & 7)
            if cmd & 0x1000:
                size = 'byte'
            else:
                size = 'word'
                ofs <<= 2
            if cmd & 0x800:
                func = 'get'  # ldr
                return [self.assign(dest, self.build(
                    'ram.get_{0}'.format(size), self.add(base, ofs), level=0))]
            else:
                func = 'set'  # str
                return [self.build('ram.set_{0}'.format(size),
                                   self.add(base, ofs), dest)]
        else:
            return [self.unknown(cmd, 2)]

    def simplify(self, parsed):
        reparsed = []
        for expr in parsed:
            # recurse
            try:
                subexpr = expr.expression
            except:
                pass
            else:
                expr.expression, = self.simplify([subexpr])
            try:
                args = expr.args
            except:
                pass
            else:
                newargs = []
                expr.args = [self.simplify([arg])[0] for arg in args]
            # remove +0, *1, <<0 ,etc.
            try:
                oper = expr.operator
                args = expr.args
            except:
                pass
            else:
                if oper in ('+', '-', '<<', '>>'):
                    args = [arg for arg in args if arg != 0]
                elif oper in ('*', ):
                    args = [arg for arg in args if arg != 1]
                if len(args) == 1:
                    reparsed.append(args[0])
                    continue
            reparsed.append(expr)
        return reparsed
