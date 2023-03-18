from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Generator, Literal
from ssmal.lang.ssmalloc.metadata.jit.codegen.string_table import StringTable

from ssmal.util.writer.line_writer import LineWriter

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo

# fmt: off

class ExpressionCompiler:
    line_writer: LineWriter
    scope: Scope
    get_type: Callable[[ast.expr], TypeInfo]
    string_table: StringTable
    _i: int = 0
    ci = CompilerInternals()

    def __init__(self, assembler_writer: LineWriter, scope: Scope, get_type: Callable[[ast.expr], TypeInfo], string_table: StringTable) -> None:
        self.line_writer = assembler_writer
        self.get_type = get_type
        self.string_table = string_table
        self.scope = scope

    def get_label(self, expr: ast.expr) -> str:
        label = f"label_for_line_{expr.lineno}_col_{expr.col_offset}__{self._i}"
        self._i += 1
        return label
    
    # def ld_stack_offset(self, offset: int, clobber_B=False):
    #     ci = self.ci
    #     yield ci.MOVSA; yield ci.PSHA; yield ci.MOVSA; yield ci.POPA
    #     yield ci.ADDi; yield f'{offset}'
    #     yield from self.deref_A(clobber_B=clobber_B)
    
    def get_method(self, self_expr: ast.expr, method_name: str) -> None:
        """
        We assume that A holds a pointer to the vtable
        and vtable holds pointers to code
        """
        ci = self.ci
        w = self.line_writer
        value_type = self.get_type(self_expr)
        method_info = value_type.get_method_info(method_name)
        if method_info is None:
            raise CompilerError(self_expr, method_name)
        w.write_line(ci.FOLLOW_A(), ci.ADDi, f'{4*method_info.index}', ci.FOLLOW_A(), ci.COMMENT("A <- type_info.methods[index].code"))
        # A now has ptr to method implementation

    def compile_expression(self, expr: ast.expr, mode: Literal['eval','access']) -> None:
        ci = self.ci
        w = self.line_writer

        w.indent()
        w.write_line(ci.COMMENT(f"expr {expr.__class__.__name__} {expr.lineno=}"))
        match (expr):
            case ast.Attribute(value=value, attr=attr):
                self.compile_expression(value, 'eval')
                # A now points at object
                value_type = self.get_type(value)
                field_info = value_type.get_field_info(attr)
                if field_info is not None:
                    index = field_info.index
                    # yield ci.LINE(ci.ADDi, f'{4 * (index + 1)}', comment=f"attribute {attr} of {value_type.name=} {mode=}")
                    w.write_line(ci.ADDi, f'{4 * (index + 1)}', ci.COMMENT(f"attribute {attr} of {value_type.name=} {mode=}"))
                    # A now points at field
                    if mode == 'eval':
                        w.write_line(ci.FOLLOW_A())
                else:
                    raise CompilerError(value, attr, expr)
            
            case ast.BinOp(left=left, right=right, op=op) if mode == 'eval':
                self.compile_expression(left, mode)
                w.write_line(self.scope.push_A(), ci.COMMENT("TOP <- left"))
                self.compile_expression(right, mode)
                w.write(ci.SWPAB, self.scope.pop_A(), ' ')

                match op:
                    case ast.Add():     w.write_line(ci.ADDB, ci.COMMENT("B <- right, A <- left"))
                    case ast.Sub():     w.write_line(ci.SUBB, ci.COMMENT("B <- right, A <- left"))
                    case ast.Div():     w.write_line(ci.DIVB, ci.COMMENT("B <- right, A <- left"))
                    case ast.Mult():    w.write_line(ci.MULB, ci.COMMENT("B <- right, A <- left"))
                    case _:             raise CompilerError(expr)

            case ast.BoolOp(values=values, op=op) if mode == 'eval':
                short_circuit_label = self.get_label(expr)
                for value in values:
                    continue_label = self.get_label(expr)
                    self.compile_expression(value, mode)
                    # value in register A
                    match op:
                        case ast.And():
                            w.write_line(ci.BRZi, ci.GOTO_LABEL(short_circuit_label), ci.COMMENT('fail'))
                        case ast.Or():
                            w.write_line(ci.BRZi, ci.GOTO_LABEL(continue_label), ci.COMMENT('success'))
                            w.write_line(ci.BRZi, ci.GOTO_LABEL(continue_label), ci.COMMENT('fail'))
                    w.write_line(ci.MARK_LABEL(continue_label))

                w.write_line(ci.MARK_LABEL(short_circuit_label))
            
            case ast.Call(func=ast.Name(id='print') as func, args=[arg]) if mode == 'eval':
                self.compile_expression(arg, mode='eval')
                w.write(ci.PSHA, ' ')
                arg_type = self.get_type(arg)
                _PTOP = -1
                match arg_type.name:
                    case 'int': _PTOP = ci.PTOPi
                    case 'str': _PTOP = ci.PTOPz
                    case _: raise CompilerError(func)

                w.write_line(ci.LDAi, f'{_PTOP}', ci.SYS, ci.COMMENT('print()'))

            case ast.Call(func=ast.Attribute(value=self_expr, attr=method_name) as func, args=args) if mode == 'eval':
                # CALLING CONVENTION: [CALL]
                # save return address
                w.write_line(ci.SWPAI, ci.PSHA, ci.SWPAI, ci.COMMENT('save return address'))
                self.compile_expression(self_expr, mode='eval')
                w.write_line(ci.PSHA, ci.COMMENT('save self'))
                for i,arg in enumerate(args):
                    self.compile_expression(arg, 'eval')
                    w.write_line(ci.PSHA, ci.COMMENT(f'save args[{i}]'))
                w.write_line(ci.MOVSA, ci.SUBi, f'{4 * (len(args) + 1)}', ci.SWPAB, ci.LDAb, ci.COMMENT("A <- self"))
                self.get_method(self_expr, method_name)
                w.write_line(ci.BRa, ci.COMMENT(f'goto {method_name}'))

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value) if mode == 'eval':
                match value:
                    case None:          w.write_line(ci.LDAi, ci.NONE, ci.COMMENT('CONST None'))
                    case str(val):      w.write_line(ci.LDAi, ci.ZSTR(val), ci.COMMENT('CONST str'))
                    case bytes(val):    raise CompilerError(val)
                    case True:          w.write_line(ci.LDAi, ci.TRUE, ci.COMMENT('CONST True'))
                    case False:         w.write_line(ci.LDAi, ci.FALSE, ci.COMMENT('CONST False'))
                    case int(val):      w.write_line(ci.LDAi, f'{val}', ci.COMMENT('CONST int'))
                    case float(val):    raise CompilerError(val)
                    case complex(val):  raise CompilerError(val)
                    case _:             raise CompilerError(value)

            case ast.Name(id=id):
                self.scope.access_variable(w, id, mode)
            
            case _: raise CompilerError(expr)
        
        w.dedent()
