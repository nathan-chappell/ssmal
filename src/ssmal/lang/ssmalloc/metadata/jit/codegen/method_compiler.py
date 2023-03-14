from __future__ import annotations

import ast
from collections import OrderedDict
from dataclasses import dataclass, field
import inspect
import logging
import textwrap
from typing import Generator, Literal, TypeGuard, cast

from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_error import CompilerError
from ssmal.lang.ssmalloc.metadata.jit.codegen.compiler_internals import CompilerInternals
from ssmal.lang.ssmalloc.metadata.jit.codegen.expression_compiler import ExpressionCompiler
from ssmal.lang.ssmalloc.metadata.jit.codegen.scope import Scope
from ssmal.lang.ssmalloc.metadata.jit.strongly_typed_strings import Identifier, TypeName
from ssmal.lang.ssmalloc.metadata.jit.type_info import MethodInfo, TypeInfo, TypeInfoBase, int_type, str_type


log = logging.getLogger(__name__)


class TypeError(CompilerError):
    ...


# fmt: off

class MethodCompiler:
    ci = CompilerInternals()
    type_dict: OrderedDict[TypeName, TypeInfo]
    variable_types: OrderedDict[Identifier, TypeInfo]
    self_type: TypeInfo

    def __init__(self, type_dict: OrderedDict[TypeName, TypeInfo], self_type: TypeInfo) -> None:
        self.self_type = self_type
        self.type_dict = type_dict
        self.variable_types = OrderedDict[Identifier, TypeInfo]()
        # self.variable_types[Identifier('self')] = self_type
    
    def is_typename(self, name: str) -> TypeGuard[TypeName]:
        return name in self.type_dict

    def is_identifier(self, name: str) -> TypeGuard[Identifier]:
        return name in self.variable_types
    
    def reset_variable_types(self, method_info: MethodInfo):
        self.variable_types = OrderedDict[Identifier, TypeInfo]()
        self.variable_types[Identifier('self')] = self.self_type
        for param in method_info.parameters:
            self.variable_types[Identifier(param.name)] = param.type
    
    def compile_method(self, method_info: MethodInfo) -> Generator[str, None, None]:
        ci = self.ci

        function_def = ast.parse(textwrap.dedent(inspect.getsource(method_info.method))).body[0]

        if isinstance(function_def, ast.FunctionDef):
            # create scope
            scope = Scope(function_def)
            expression_compiler = ExpressionCompiler(scope, self.infer_type)
            
            # CALLING CONVENTION: [ANSWER]
            yield ci.STAi; yield f'{0}'
            for _ in range(len(scope.locals)):
                yield ci.PSHA

            for stmt in function_def.body:
                log.debug(f'{stmt=}')
                yield f"; |> {stmt=} {stmt.lineno=}\n"
                match stmt:
                    case ast.AnnAssign(target=ast.Name(id=variable_name), annotation=ast.Name(id=type_name), value=value):
                        if variable_name not in scope.offsets:
                            raise CompilerError(stmt)
                        if not self.is_typename(type_name):
                            raise TypeError(type_name, stmt)
                        target_type = self.type_dict[type_name]
                        self.variable_types[Identifier(variable_name)] = target_type
                        if value is not None:
                            value_type = self.infer_type(value)
                            if not self.is_subtype(value_type, target_type):
                                raise TypeError(value_type, target_type, stmt)
                            yield from expression_compiler.compile_expression(value, 'eval'); yield ci.SWPAB
                            yield from scope.access_variable(variable_name, 'access')
                            yield ci.SWPAB; yield ci.STAb
                    
                    case ast.Assign(targets=[target], value=value):
                        target_type = self.infer_type(target)
                        value_type = self.infer_type(value)
                        if not self.is_subtype(value_type, target_type):
                            raise TypeError(value_type, target_type, stmt)
                        yield from expression_compiler.compile_expression(value, 'eval')
                        yield from scope.push_A()
                        yield from expression_compiler.compile_expression(target, 'access')
                        yield ci.SWPAB; yield from scope.pop_A(); yield ci.SWPAB; yield ci.STAb
                        
                    case ast.Expr(expr):
                        self.infer_type(expr)
                        yield from expression_compiler.compile_expression(expr, 'eval')
                    
                    # case ast.If(expr):
                    #     self.infer_type(expr)
                    #     yield from expression_compiler.compile_expression(expr, 'eval')
                    
                    case ast.Return(value=expr):
                        if expr is None:
                            raise CompilerError(expr, stmt)
                        returned_type = self.infer_type(expr)
                        if not self.is_subtype(returned_type, method_info.return_type):
                            raise CompilerError(stmt)
                        yield from expression_compiler.compile_expression(expr, 'eval')
                    
                    case _:
                        raise CompilerError(stmt)
                
                yield f"; |< {stmt=} {stmt.lineno=}\n"
            
            # CALLING CONVENTION: [RETURN]
            # save A (result)
            yield ci.SWPAB
            yield ' '.join(ci.POPA for _ in range(len(scope.locals)))
            yield ' '.join(ci.POPA for _ in range(len(scope.args)))
            yield ci.POPA; yield ci.SWPAB; yield ci.BRb
            # A has result, B has return address
        else:
            raise CompilerError(method_info)
    
    def infer_type(self, expr: ast.expr) -> TypeInfo:
        match expr:
            case ast.Attribute(value=value, attr=method_attr):
                value_type = self.infer_type(value)
                field_info = value_type.get_field_info(method_attr)
                if field_info is not None:
                    return field_info.type
                else:
                    raise TypeError(f'Invalid field {method_attr}', expr)
            
            case ast.BinOp(left=left, right=right) if all(self.infer_type(operand) == int_type for operand in [left, right]): return int_type
        
            case ast.BinOp(): raise TypeError(f'Operation not supported', expr)

            case ast.BoolOp(values=values) if all([self.infer_type(value) == int_type for value in values]): return int_type

            case ast.BoolOp(values=values): raise TypeError(f'Operation not supported', expr)
            
            case ast.Call(func=ast.Name(id="print"), args=args):
                for arg in args:
                    self.infer_type(arg)
                return int_type

            case ast.Call(func=ast.Attribute() as method_attr, args=args):
                method_info = self.infer_method(method_attr)
                if method_info.parent != self.self_type:
                    raise TypeError('Invalid method lookup', method_info, self.self_type, method_attr)
                arg_types = [self.infer_type(arg) for arg in args]
                for parameter, arg_type in zip(method_info.parameters, arg_types):
                    if not self.is_subtype(arg_type, parameter.type):
                        raise TypeError(f"{arg_type=} is not a subtype of {parameter.type=}", parameter, method_attr)
                return method_info.return_type
            
            case ast.Constant(value=value):
                match value:
                    case None:          return int_type
                    case str():         return str_type
                    case bytes(val):    raise TypeError(val)
                    case True:          return int_type
                    case False:         return int_type
                    case int():         return int_type
                    case float(val):    raise TypeError(val)
                    case complex(val):  raise TypeError(val)
                    case _:             raise TypeError(value)

            case ast.Name(id=id) if self.is_identifier(id): return self.variable_types[id]
            
            case ast.Name(id=id): raise TypeError(f'Missing variable {id}', expr)

            case _: raise TypeError(expr)
                    
    
    def infer_method(self, attr: ast.Attribute) -> MethodInfo:
        method_name = attr.attr
        value_type = self.infer_type(attr.value)
        method_info = value_type.get_method_info(method_name)
        if method_info is not None:
            return method_info
        else:
            raise TypeError(f'{method_name=} not found on {value_type.name=}', value_type, attr)
                
    
    def is_subtype(self, l: TypeInfo, r: TypeInfo) -> bool:
        parent: TypeInfoBase | None = l
        for _ in range(20):
            if parent == r:
                return True
            elif parent is None:
                return False
            else:
                parent = parent.parent
        else:
            raise TypeError("Maximum is_subtype recursing reached")
