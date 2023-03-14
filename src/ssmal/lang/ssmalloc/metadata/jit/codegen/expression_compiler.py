from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Generator, Literal

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.type_info import TypeInfo

# fmt: off

class ExpressionCompiler:
    scope: Scope
    get_type: Callable[[ast.expr], TypeInfo]
    _i: int = 0
    ci = CompilerInternals()

    def __init__(self, scope: Scope, get_type: Callable[[ast.expr], TypeInfo]) -> None:
        self.scope = scope
        self.get_type = get_type

    def get_label(self, expr: ast.expr) -> str:
        label = f"label_for_line_{expr.lineno}_col_{expr.col_offset}__{self._i}"
        self._i += 1
        return label
    
    # def deref_A(self, clobber_B=False) -> Generator[str, None, None]:
    #     ci = self.ci
    #     yield ci.SWPAB
    #     if not clobber_B:
    #         yield ci.PSHA
    #     # deref A
    #     yield ci.LDAb
    #     if not clobber_B:
    #         # restore B
    #         yield ci.SWPAB; yield ci.POPA; yield ci.SWPAB
        
    def ld_stack_offset(self, offset: int, clobber_B=False):
        ci = self.ci
        yield ci.MOVSA; yield ci.PSHA; yield ci.MOVSA; yield ci.POPA
        yield ci.ADDi; yield f'{offset}'
        yield from self.deref_A(clobber_B=clobber_B)
    
    def get_method(self, self_expr: ast.expr, method_name: str) -> Generator[str, None, None]:
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

    def compile_expression(self, expr: ast.expr, mode: Literal['eval','access']) -> Generator[str, None, None]:
        ci = self.ci

        yield f"; |> {expr=} {expr.lineno=}\n"
        match (expr):
            case ast.Attribute(value=value, attr=attr):
                yield from self.compile_expression(value, 'eval')
                # A now points at object
                value_type = self.get_type(value)
                field_info = value_type.get_field_info(attr)
                if field_info is not None:
                    index = field_info.index
                    yield ci.ADDi; yield f'{4 * (index + 1)}'
                    # A now points at field
                    if mode == 'eval':
                        yield ci.FOLLOW_A()
                else:
                    raise CompilerError(value, attr, expr)
            
            case ast.BinOp(left=left, right=right, op=op) if mode == 'eval':
                yield from self.compile_expression(left, mode)
                yield ci.PSHA
                yield from self.compile_expression(right, mode)
                yield ci.SWPAB
                yield ci.POPA

                match op:
                    case ast.Add():     yield ci.ADDB
                    case ast.Sub():     yield ci.SUBB
                    case ast.Div():     yield ci.MULB
                    case ast.Mult():    yield ci.DIVB
                    case _:             raise CompilerError(expr)

            case ast.BoolOp(values=values, op=op) if mode == 'eval':
                short_circuit_label = self.get_label(expr)
                for value in values:
                    continue_label = self.get_label(expr)
                    yield from self.compile_expression(value, mode)
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
            
            case ast.Call(func=ast.Name(id='print') as func, args=[arg]) if mode == 'eval':
                yield from self.compile_expression(arg, mode='eval'); yield ci.PSHA
                arg_type = self.get_type(arg)
                
                if arg_type.name == 'int':
                    yield ci.LDAi; yield f'{ci.PTOPi}'; yield ci.SYS
                elif arg_type.name == 'str':
                    yield ci.LDAi; yield f'{ci.PTOPz}'; yield ci.SYS
                else:
                    raise CompilerError(func)

            case ast.Call(func=ast.Attribute(value=self_expr, attr=method_name) as func, args=args) if mode == 'eval':
                # CALLING CONVENTION: [CALL]
                # save return address
                yield ci.SWPAI; yield ci.PSHA; yield ci.SWPAI
                yield from self.compile_expression(self_expr, mode='eval'); yield ci.PSHA
                for arg in args:
                    yield from self.compile_expression(arg, 'eval'); yield ci.PSHA
                yield from self.get_method(self_expr, method_name); yield ci.BRa

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value) if mode == 'eval':
                match value:
                    case None:          yield ci.NONE
                    case str(val):      yield ci.ZSTR(val)
                    case bytes(val):    raise CompilerError(val)
                    case True:          yield ci.TRUE
                    case False:         yield ci.FALSE
                    case int(val):      yield f'{val}'
                    case float(val):    raise CompilerError(val)
                    case complex(val):  raise CompilerError(val)
                    case _:             raise CompilerError(value)

            case ast.Name(id=id):
                yield from self.scope.access_variable(id, mode)
            
            case _: raise CompilerError(expr)
        
        yield f"; |< {expr=} {expr.lineno=}\n"
