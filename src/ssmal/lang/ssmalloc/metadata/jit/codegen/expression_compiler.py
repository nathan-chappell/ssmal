from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Generator

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals


class ExpressionCompiler:
    _i: int = 0
    ci = CompilerInternals()

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
                yield ci.SWPAB
                yield ci.POPA

                match op:
                    case ast.Add():
                        yield ci.ADDB
                    case ast.Sub():
                        yield ci.SUBB
                    case ast.Div():
                        yield ci.MULB
                    case ast.Mult():
                        yield ci.DIVB
                    case _:
                        raise CompilerError(expr)

            case ast.BoolOp(values=values, op=op):
                short_circuit_label = self.get_label(expr)
                for value in values:
                    continue_label = self.get_label(expr)
                    yield from self.compile_expression(value)
                    # value in register A
                    match op:
                        case ast.And():
                            yield ci.BRZi
                            yield ci.GOTO_LABEL(short_circuit_label)
                        case ast.Or():
                            yield ci.BRZi
                            yield ci.GOTO_LABEL(continue_label)
                            yield ci.BRi
                            yield ci.GOTO_LABEL(short_circuit_label)
                    yield ci.MARK_LABEL(continue_label)

                yield ci.MARK_LABEL(short_circuit_label)

            case ast.Call():
                ...

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value):
                match value:
                    case None:
                        yield ci.NONE
                    case str(str_literal):
                        yield ci.ZSTR(str_literal)
                    case bytes(bytes_literal):
                        yield bytes_literal
                    case True:
                        yield ci.TRUE()
                    case False:
                        yield ci.FALSE
                    case int(int_literal):
                        yield ci.TO_BYTES(int_literal)
                    case float(float_literal):
                        raise CompilerError(float_literal)
                    case complex(complex_literal):
                        raise CompilerError(complex_literal)
                    case _:
                        raise CompilerError(value)

            case ast.Name():
                ...
