
from compileengine import Decompiler, Variable


class SBC(Decompiler):
    matrices = {}

    def parse_next(self):
        cmd = self.read_value(1)
        if not cmd:
            return []
        elif cmd == 0x1:
            return [self.end()]
        elif cmd == 0x2:
            node_id = self.read_value(1)
            visible = bool(self.read_value(1))
            return [self.func('node', node_id, visible)]
        elif cmd == 0b11:
            matrix_id = self.read_value(1)
            return [self.func('matrix', matrix_id)]
        elif cmd == 0b100:
            material_id = self.read_value(1)
            return [self.func('material', material_id)]
        elif cmd == 0b101:
            shape_id = self.read_value(1)
            return [self.func('shape', shape_id)]
        elif cmd == 0b110:
            opt = cmd >> 5
            node_id = self.read_value(1)
            parent_id = self.read_value(1)
            value = self.read_value(1)
            args = [node_id, parent_id, value]
            dest = None
            if opt & 0b01:
                dest = self.get_matrix()
            if opt & 0b10:
                src = self.get_matrix()
                args += src
            expr = self.func('node_desc', *args)
            if dest is not None:
                expr = self.assign(dest, expr)
            return [expr]
        elif cmd == 0b111:
            opt = cmd >> 5
            node_id = self.read_value(1)
            args = [node_id]
            dest = None
            if opt & 0b01:
                dest = self.get_matrix()
            if opt & 0b10:
                src = self.get_matrix()
                args += src
            expr = self.func('billboard', *args)
            if dest is not None:
                expr = self.assign(dest, expr)
            return [expr]
        elif cmd & 0b11111 == 0b01011:
            opt = cmd >> 5
            if opt == 0:
                return [self.func('scale')]
            elif opt == 1:
                return [self.func('inv_scale')]
            else:
                raise ValueError('Unknown scale op')
        return [self.unknown(cmd, 1)]

    def get_matrix(self, matrix_id=None):
        if matrix_id is None:
            matrix_id = self.read_value(1)
        if matrix_id not in self.matrices:
            mtx = Variable(matrix_id)
            mtx.persist = True
            mtx.name = 'matrix[{0}]'.format(matrix_id)
            self.matrices[matrix_id] = mtx
            return mtx
        else:
            return self.matrices[matrix_id]

