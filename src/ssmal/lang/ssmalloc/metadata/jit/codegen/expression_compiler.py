from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Callable, Generator, Literal
from ssmal.lang.ssmalloc.metadata.jit.codegen.calling_convention import CallingConvention

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
    cc: CallingConvention

    def __init__(self, scope: Scope, get_type: Callable[[ast.expr], TypeInfo]) -> None:
        self.scope = scope
        self.get_type = get_type
        self.cc = CallingConvention(self.compile_expression, self.scope)

    def get_label(self, expr: ast.expr) -> str:
        label = f"label_for_line_{expr.lineno}_col_{expr.col_offset}__{self._i}"
        self._i += 1
        return label

    def compile_expression(self, expr: ast.expr, mode: Literal['eval','access']) -> Generator[str, None, None]:
        ci = self.ci
        cc = self.cc

        def _deref_A(clobber_B=False) -> Generator[str, None, None]:
            yield ci.SWPAB
            if not clobber_B:
                yield ci.PSHA
            # deref A
            yield ci.LDAb
            if not clobber_B:
                # restore B
                yield ci.SWPAB; yield ci.POPA; yield ci.SWPAB
        
        def _ld_stack_offset(offset: int, clobber_B=False):
            yield ci.SWPAS; yield ci.PSHA; yield ci.SWPAS; yield ci.POPA
            yield ci.ADDi; yield f'{offset}'
            yield from _deref_A(clobber_B=clobber_B)
        
        def _get_method(func_expr: ast.expr) -> Generator[str, None, None]:
            match func_expr:
                # case ast.Name(id='print'):
                #     ...
                case ast.Attribute(value=value, attr=attr):
                    yield from self.compile_expression(value, 'access')
                    yield from _deref_A(clobber_B=True)
                    # A now points at type info...
                    METHODS_ARRAY_OFFSET = 3
                    CODE_OFFSET = 4
                    yield ci.ADDi; yield f'{4*METHODS_ARRAY_OFFSET}'; yield from _deref_A(clobber_B=True); yield ci.PSHA
                    # A now points at methods array object, saved on stack
                    yield from _deref_A(clobber_B=True); yield ci.PSHA
                    # A now has array size, saved on stack
                    yield from _ld_stack_offset(-8) # methods array object
                    yield ci.ADDi; yield f'{4}'; yield from _deref_A(clobber_B=True)
                    # A now has ptr to method info
                    value_type = self.get_type(value)
                    for index, method_info in enumerate(value_type.methods):
                        if method_info.name == attr:
                            break
                    else:
                        raise CompilerError(value_type, attr, func_expr)
                    # use index to access vtable...
                    yield ci.ADDi; yield f'{4 * (index)}'; yield from _deref_A(clobber_B=True)
                    # access code
                    yield ci.ADDi;  yield f'{4 * CODE_OFFSET}'; yield from _deref_A(clobber_B=True)
                    # A now has ptr to method implementation
                case _:
                    raise CompilerError(func_expr)

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
                        yield from _deref_A()
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


            case ast.Call(func=ast.Attribute() as func, args=args) if mode == 'eval':
                yield from _get_method(func); yield ci.PSHA
                yield from self.compile_expression(func.value, mode='eval'); yield ci.PSHA
                yield from cc.call_method(func, args)

            #   value: Any  # None, str, bytes, bool, int, float, complex, Ellipsis
            case ast.Constant(value=value) if mode == 'eval':
                match value:
                    case None:          yield ci.NONE
                    case str(val):      yield ci.ZSTR(val)
                    case bytes(val):    raise CompilerError(val)
                    case True:          yield ci.TRUE
                    case False:         yield ci.FALSE
                    case int(val):      yield ci.TO_BYTES(val)
                    case float(val):    raise CompilerError(val)
                    case complex(val):  raise CompilerError(val)
                    case _:             raise CompilerError(value)

            case ast.Name(id=id):
                yield from self.scope.access_variable(id, mode)
