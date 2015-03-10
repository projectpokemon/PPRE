
from compileengine import Decompiler


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
        cmd = self.read_value(4)
        return [self.unknown(cmd, 4)]

    def parse(self):
        """Read expressoin until return

        """
        while True:
            cmd_parts = self.parse_next()

            # TODO: logic
            break
        return self.lines
