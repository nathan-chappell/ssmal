from dataclasses import dataclass

TypeName = str
Identifier = str


class SimpleAstNodeBase:
    ...


class Statement(SimpleAstNodeBase):
    ...


class Expression(SimpleAstNodeBase):
    ...


@dataclass
class CallExpr(Expression):
    function_name: Identifier
    arguments: list["Identifier | CallExpr"]


@dataclass
class AssignmentStmt(Statement):
    target_variable: Identifier
    value: Identifier | CallExpr


@dataclass
class ClassDef(Statement):
    name: TypeName
    bases: tuple[TypeName]


@dataclass
class FunctionDef(Statement):
    parameter_types: tuple[TypeName]
    return_type: TypeName


@dataclass
class VariableDef(Statement):
    name: Identifier
    type: TypeName


@dataclass
class Program(SimpleAstNodeBase):
    statements: list[Statement]
