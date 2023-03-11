from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Generator

class CompilerError(Exception):
    ...

# fmt: off

class CompilerInternals:

    NOP     = "NOP"
    DBG     = "DBG"
    HALT    = "HALT"
    # arithmetic ops
    ADDB    = "ADDB"
    SUBB    = "SUBB"
    MULB    = "MULB"
    DIVB    = "DIVB"
    ADDi    = "ADDi"
    SUBi    = "SUBi"
    MULi    = "MULi"
    DIVi    = "DIVi"
    ADD_    = "ADD_"
    SUB_    = "SUB_"
    MUL_    = "MUL_"
    DIV_    = "DIV_"
    # data ops
    LDAi    = "LDAi"
    LDAb    = "LDAb"
    LDA_    = "LDA_"
    STAi    = "STAi"
    STAb    = "STAb"
    STA_    = "STA_"
    # stack ops
    PSHA    = "PSHA"
    POPA    = "POPA"
    CALi    = "CALi"
    CALA    = "CALA"
    CAL_    = "CAL_"
    RETN    = "RETN"
    # syscall - must be added later so that io can be put in...
    SYS     = "SYS"
    # register ops
    SWPAB   = "SWPAB"
    SWPAI   = "SWPAI"
    SWPAS   = "SWPAS"
    # branch ops
    BRi     = "BRi"
    BRa     = "BRa"
    BRZi    = "BRZi"
    BRNi    = "BRNi"
    BRZb    = "BRZb"
    BRNb    = "BRNb"

    NULL_TERMINATOR = b'\x00'
    NONE = bytes.fromhex('00000000')
    FALSE = bytes.fromhex('00000000')

    BYTE_ORDER = 'little'

    @classmethod
    def ZSTR(cls, s: str) -> bytes: return bytes(s, encoding="ascii") + cls.NULL_TERMINATOR

    @classmethod
    def GOTO_LABEL(cls, s: str) -> str: return f'${s}'

    @classmethod
    def MARK_LABEL(cls, s: str) -> str: return f'.{s}'

    @classmethod
    def TO_BYTES(cls, z: int) -> bytes: return z.to_bytes(4, cls.BYTE_ORDER, signed=True)

    @classmethod
    def TRUE(cls) -> bytes: return cls.TO_BYTES(1)

    
class ExpressionCompiler:
    _i: int = 0
    ci: CompilerInternals = CompilerInternals()

    def get_label(self, expr: ast.expr) -> str:
        label = f"label_for_line_{expr.lineno}_col_{expr.col_offset}__{self._i}"
        self._i += 1
        return label

    def compile_expression(self, expr: ast.expr) -> Generator[str | bytes, None, None]:
        ci = self.ci        

        match (expr):
            case ast.Attribute():
                ...

            case ast.BinOp(left=left, right=right, op=op):
                yield from self.compile_expression(left)
                yield ci.PSHA
                yield from self.compile_expression(right)
                yield ci.SWPAB; yield ci.POPA

                match op:
                    case ast.Add():     yield ci.ADDB
                    case ast.Sub():     yield ci.SUBB
                    case ast.Div():     yield ci.MULB
                    case ast.Mult():    yield ci.DIVB
                    case _:             raise CompilerError(expr)

            case ast.BoolOp(values=values, op=op):
                short_circuit_label = self.get_label(expr)
                for value in values:
                    continue_label = self.get_label(expr)
                    yield from self.compile_expression(value)
                    # value in register A
                    match op:
                        case ast.And():
                            yield ci.BRZi;  yield ci.GOTO_LABEL(short_circuit_label)
                        case ast.Or():
                            yield ci.BRZi;  yield ci.GOTO_LABEL(continue_label)
                            yield ci.BRi;   yield ci.GOTO_LABEL(short_circuit_label)
                    yield ci.MARK_LABEL(continue_label)
                        
                yield ci.MARK_LABEL(short_circuit_label)

            case ast.Call():
                ...

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value):
                match value:
                    case None:                      yield ci.NONE
                    case str(str_literal):          yield ci.ZSTR(str_literal)
                    case bytes(bytes_literal):      yield bytes_literal
                    case True:                      yield ci.TRUE()
                    case False:                     yield ci.FALSE
                    case int(int_literal):          yield ci.TO_BYTES(int_literal)
                    case float(float_literal):      raise CompilerError(float_literal)
                    case complex(complex_literal):  raise CompilerError(complex_literal)
                    case _:                         raise CompilerError(value)

            case ast.Expr():
                ...

            case ast.Name():
                ...