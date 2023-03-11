from __future__ import annotations

import ast
import inspect
from pprint import pprint
import textwrap

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Callable, Generator, Literal, NewType

from ssmal.lang.ssmalloc.metadata.type_info import TypeInfo


def dump_ast(node: ast.AST, indent=0, prefix=""):
    def _indent(s: Any, marker: str = None):
        # return "    " * indent + f'[{prefix}]\t' + str(s)
        # pf = f'<{prefix}>'
        pf = f"{prefix}"
        _s = str(s)
        padding = max(4, 60 - len(pf)) * " "
        line = f"{pf}{padding}{_s}"
        if marker is not None:
            line = marker + line[len(marker) :]
        return line

    print(_indent(f"> {node.__class__.__name__}", marker=">"))
    for _field in node._fields:
        _prefix = f"{prefix}.{_field}"
        _field_node = getattr(node, _field)
        if isinstance(_field_node, list) and _field_node:
            # dump_ast(_sub_field, indent=indent + 1, prefix=f"{_prefix}[]")
            _array_prefix = f"{_prefix}[{{index}}]"
            _sub_prefix = " " * len(_array_prefix)
            # print(_indent(f"{_field_node}{_prefix}[]"))
            print(_field, end=" > ")
            pprint(_field_node)
            for i, _sub_field in enumerate(_field_node):
                dump_ast(_sub_field, indent=indent + 1, prefix=_array_prefix.format(index=i))
        elif isinstance(_field_node, ast.AST):
            dump_ast(_field_node, prefix=_prefix)
        else:
            print(_indent(f'  {_field} = | {_field_node} | {_field_node.__class__.__name__} |'))
    print(_indent(f"< {node}", marker="<"))


FullName = NewType("FullName", str)
Identifier = NewType("Identifier", str)
TypeName = NewType("TypeName", Identifier)


@dataclass
class SmallocNode:
    ast_node: ast.AST


@dataclass
class Parameter(SmallocNode):
    name: Identifier
    type: TypeName


@dataclass
class Statement(SmallocNode):
    ...


@dataclass
class Expression(Statement):
    ...


@dataclass
class Const(Expression):
    value: str | int
    type: Literal["int", "str"]


@dataclass
class Variable(Expression):
    name: Identifier
    type: TypeName


@dataclass
class IndexAccess(Expression):
    _self: LValue
    index: Variable | Const


@dataclass
class FieldAccess(Expression):
    _self: LValue
    field_name: Identifier


@dataclass
class FunctionCall(Expression):
    function: LValue
    args: list[Expression]


LValue = Variable | IndexAccess | FieldAccess


@dataclass
class Declaration(Statement):
    variable: Variable
    value: Expression | None


@dataclass
class Assignment(Statement):
    lhs: LValue
    rhs: Expression


@dataclass
class Return(Statement):
    value: Expression


@dataclass
class MethodDef(Statement):
    name: Identifier
    parameters: list[Parameter]
    return_type: TypeName
    body: list[Statement]


class ParseError(Exception):
    ...


class JitParser:
    type_cache: OrderedDict[str, TypeInfo]

    def __init__(self, type_cache: OrderedDict[str, TypeInfo]) -> None:
        self.type_cache = type_cache

    def get_method_def(self, method_def: Callable) -> ast.FunctionDef:
        _module = ast.parse(textwrap.dedent(inspect.getsource(method_def)))
        _function_def = _module.body[0]
        if not isinstance(_function_def, ast.FunctionDef):
            raise ParseError(f"Invalid method def: {method_def}", method_def)

        return _function_def

    def parse_method_def(self, method_def: ast.FunctionDef) -> MethodDef:
        name: Identifier = Identifier(method_def.name)
        parameters: list[Parameter] = list(self.parse_parameters(method_def.args))
        match method_def.returns:
            case ast.Name(id=_return_type):
                pass
            case _returns:
                raise ParseError(method_def, _returns)
        # if not isinstance(expr, string)
        return_type: TypeName = TypeName(Identifier(_return_type))
        body: list[Statement] = self.parse_method_body(method_def.body)

        return MethodDef(ast_node=method_def, name=name, parameters=parameters, body=body, return_type=return_type)

    def parse_parameters(self, arguments: ast.arguments) -> Generator[Parameter, None, None]:
        if arguments.vararg or arguments.kwonlyargs or arguments.kw_defaults or arguments.kwarg or arguments.defaults:
            raise ParseError(arguments)
        for arg in arguments.args:
            match arg:
                case ast.arg(arg="self"):
                    pass
                case ast.arg(arg=_name, annotation=ast.Name(id=_type_name)):
                    yield Parameter(arg, Identifier(_name), TypeName(Identifier(_type_name)))
                case _:
                    raise ParseError(arg)

    def parse_method_body(self, body: list[ast.stmt]) -> Generator[Statement, None, None]:
        for stmt in body:
            match stmt:
                case ast.Assign(): ...
                case ast.AugAssign(): ...
                case ast.AnnAssign(): ...
                case ast.expr(value=ast.Call()): ...
                case _:
                    raise ParseError(stmt)

if __name__ == "__main__":
    jit = JitParser(OrderedDict())
    # _get_method_def = jp.get_method_def(JitParser.get_method_def)
    from ssmal.lang.ssmalloc.stdlib.TypeInfo import TypeInfoBase

    method_def = jit.get_method_def(TypeInfoBase.print)
    dump_ast(method_def)
