import typing as T
from dataclasses import dataclass

Identifier = T.NewType("Identifier", str)
TypeName = T.NewType("TypeName", str)


class SimpleAstNodeBase:
    ...


class Statement(SimpleAstNodeBase):
    ...


class Expression(SimpleAstNodeBase):
    ...


@dataclass
class IdentifierExpr(Expression):
    identifier: Identifier


@dataclass
class ValueExpr(Expression):
    value: str | int


@dataclass
class CallExpr(Expression):
    function_name: Identifier
    arguments: list[Expression]


@dataclass
class AssignmentStmt(Statement):
    target_variable: Identifier
    value: Expression


@dataclass
class ClassDef(Statement):
    name: TypeName
    base: TypeName | None = None


@dataclass
class FunctionDef(Statement):
    name: Identifier
    parameter_types: list[TypeName]
    return_type: TypeName


@dataclass
class VariableDef(Statement):
    name: Identifier
    type: TypeName


# @dataclass
# class TypeAlias(Statement):
#     name: Identifier
#     value: Expression


@dataclass
class Program(SimpleAstNodeBase):
    statements: T.Sequence[Statement]
