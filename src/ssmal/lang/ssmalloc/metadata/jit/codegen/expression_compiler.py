from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Generator, Literal

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
    _i: int = 0
    ci = CompilerInternals()

    def __init__(self, assembler_writer: LineWriter, scope: Scope, get_type: Callable[[ast.expr], TypeInfo]) -> None:
        self.line_writer = assembler_writer
        self.get_type = get_type
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
        ci = self.ci
        yield from self.compile_expression(self_expr, 'access')
        yield ci.FOLLOW_A()
        # A now points at type info...
        METHODS_ARRAY_OFFSET = 3
        CODE_OFFSET = 4
        yield ci.ADDi; yield f'{4*METHODS_ARRAY_OFFSET}'; yield ci.FOLLOW_A(); yield ci.PSHA
        # A now points at methods array object, saved on stack
        yield ci.FOLLOW_A(); yield ci.PSHA
        # A now has array size, saved on stack
        yield from self.ld_stack_offset(-8) # methods array object
        yield ci.ADDi; yield f'{4}'; yield ci.FOLLOW_A()
        # A now has ptr to method info
        value_type = self.get_type(self_expr)
        for index, method_info in enumerate(value_type.methods):
            if method_info.name == method_name:
                break
        else:
            raise CompilerError(value_type, method_name, self_expr)
        # use index to access vtable...
        yield ci.ADDi; yield f'{4 * (index)}'; yield ci.FOLLOW_A()
        # access code
        yield ci.ADDi;  yield f'{4 * CODE_OFFSET}'; yield ci.FOLLOW_A()
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
                w.write(ci.SWPAB, self.scope.pop_A(), ci.COMMENT("B <- right, A <- left"))

                match op:
                    case ast.Add():     w.write_line(ci.ADDB)
                    case ast.Sub():     w.write_line(ci.SUBB)
                    case ast.Div():     w.write_line(ci.MULB)
                    case ast.Mult():    w.write_line(ci.DIVB)
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
                self.compile_expression(arg, mode='eval'); yield ci.PSHA
                arg_type = self.get_type(arg)
                _PTOP = -1
                match arg_type.name:
                    case 'int': _PTOP = ci.PTOPi
                    case 'str': _PTOP = ci.PTOPz
                    case _: raise CompilerError(func)

                w.write_line(ci.LDAi, f'{_PTOP}', ci.SYS)

            case ast.Call(func=ast.Attribute(value=self_expr, attr=method_name) as func, args=args) if mode == 'eval':
                # CALLING CONVENTION: [CALL]
                # save return address
                w.write_line(ci.SWPAI, ci.PSHA, ci.SWPAI, ci.COMMENT('save return address'))
                self.compile_expression(self_expr, mode='eval')
                w.write_line(ci.PSHA, ci.COMMENT('save self'))
                for i,arg in enumerate(args):
                    self.compile_expression(arg, 'eval')
                    w.write_line(ci.PSHA, ci.COMMENT(f'save args[{i}]'))
                self.get_method(self_expr, method_name)
                w.write_line(ci.BRa, ci.COMMENT(f'goto {method_name}'))

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value) if mode == 'eval':
                match value:
                    case None:          w.write(ci.NONE)
                    case str(val):      w.write(ci.ZSTR(val))
                    case bytes(val):    raise CompilerError(val)
                    case True:          w.write(ci.TRUE)
                    case False:         w.write(ci.FALSE)
                    case int(val):      w.write(f'{val}')
                    case float(val):    raise CompilerError(val)
                    case complex(val):  raise CompilerError(val)
                    case _:             raise CompilerError(value)

            case ast.Name(id=id):
                self.scope.access_variable(w, id, mode)
            
            case _: raise CompilerError(expr)
        
        w.dedent()
