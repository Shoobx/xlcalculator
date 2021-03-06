import logging

from xlfunctions import xl, math, operator, text
from . import utils

PREFIX_OP_TO_FUNC = {
    '-': operator.OP_NEG,
}

POSTFIX_OP_TO_FUNC = {
    '%': operator.OP_PERCENT,
}

INFIX_OP_TO_FUNC = {
    "*": operator.OP_MUL,
    "/": operator.OP_DIV,
    "+": operator.OP_ADD,
    "-": operator.OP_SUB,
    "^": math.POWER,
    "&": text.CONCAT,
    "=": operator.OP_EQ,
    "<>": operator.OP_NE,
    ">": operator.OP_GT,
    "<": operator.OP_LT,
    ">=": operator.OP_GE,
    "<=": operator.OP_LE,
}


class ASTNode(object):
    """A generic node in the AST"""

    def __init__(self, token):
        self.token = token

    @property
    def tvalue(self):
        return self.token.tvalue

    @property
    def ttype(self):
        return self.token.ttype

    @property
    def tsubtype(self):
        return self.token.tsubtype

    def __eq__(self, other):
        return self.token == other.token

    def eval(self, model, namespace, ref):
        raise NotImplementedError(f'`eval()` of {self}')

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"tvalue: {repr(self.tvalue)}, "
            f"ttype: {self.ttype}, "
            f"tsubtype: {self.tsubtype}"
            f">"
        )

    def __str__(self):
        return str(self.tvalue)


class OperandNode(ASTNode):

    def eval(self, model, namespace, ref):
        if self.tsubtype == "logical":
            return self.tvalue.lower() == "true"
        elif self.tsubtype in ('text', 'error'):
            return self.tvalue
        else:
            return xl.convert_number(self.tvalue)

    def __str__(self):
        if self.tsubtype == "logical":
            return self.tvalue.title()
        elif self.tsubtype == "text":
            return '"' + self.tvalue.replace('"', '\\"') + '"'
        return str(self.tvalue)


class OperatorNode(ASTNode):

    def __init__(self, token):
        super().__init__(token)
        self.left = None
        self.right = None

    def eval(self, model, namespace, ref):
        if self.ttype == 'operator-prefix':
            assert self.left is None, 'Left operand for prefix operator'
            op = PREFIX_OP_TO_FUNC[self.tvalue]
            return op(self.right.eval(model, namespace, ref))

        elif self.ttype == 'operator-infix':
            op = INFIX_OP_TO_FUNC[self.tvalue]
            return op(
                self.left.eval(model, namespace, ref),
                self.right.eval(model, namespace, ref),
            )
        elif self.ttype == 'operator-postfix':
            assert self.right is None, 'Right operand for postfix operator'
            op = POSTFIX_OP_TO_FUNC[self.tvalue]
            return op(self.left.eval(model, namespace, ref))
        else:
            raise ValueError(f'Invalid operator type: {self.ttype}')

    def __str__(self):
        left = f'({self.left}) ' if self.left is not None else ''
        right = f' ({self.right})' if self.right is not None else ''
        return f'{left}{self.tvalue}{right}'


class RangeNode(OperandNode):
    """Represents a spreadsheet cell, range, named_range."""

    def get_cells(self):
        cells = utils.resolve_ranges(self.tvalue, default_sheet='')[1]
        return cells[0] if len(cells) == 1 else cells

    @property
    def address(self):
        return self.tvalue

    def full_address(self, ref):
        addr = self.address
        if '!' not in addr:
            sheet, _, _  = utils.resolve_address(ref)
            addr = f'{sheet}!{addr}'
        return addr

    def eval(self, model, namespace, ref):
        addr = self.full_address(ref)

        if addr in model.cells:
            return model.cells[addr].value

        if addr in model.ranges:
            range_cells = []
            for range_column in model.ranges[addr].cells:
                row = []
                for cell_addr in range_column:
                    row.append(model.cells[cell_addr].value)
                range_cells.append(row)

            model.ranges[addr].value = data = xl.RangeData(range_cells)
            return data


class FunctionNode(ASTNode):
    """AST node representing a function call"""

    def __init__(self, token):
        super().__init__(token)
        self.args = None

    def eval(self, model, namespace, ref):
        func_name = self.tvalue.upper()
        # Remove the BBB namespace, since we are just supporting
        # everything in one large one.
        func_name = func_name.replace('_XLFN.', '')
        func = namespace[func_name]
        return func(
            *[arg.eval(model, namespace, ref) for arg in self.args]
        )

    def __str__(self):
        args = ', '.join(str(arg) for arg in self.args)
        return f'{self.tvalue}({args})'
