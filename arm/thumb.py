
from compileengine.assembler import Disassembler


class Thumb(Disassembler):
    stack = []

    @staticmethod
    def get_regs(data):
        regs = []
        for i in range(16):
            if data & (1 << i):
                regs.append('r{0}'.format(i))
        return regs

    @staticmethod
    def get_reg(data, high=False):
        if high:
            data += 8
        if data == 14:
            return 'engine.lr'
        return 'engine.r{0}'.format(data)

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
                    regs.append('pc')
            else:
                func = 'push'
                if cmd & 0x100:
                    regs.append('lr')
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
            if reg == 'engine.lr':
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
