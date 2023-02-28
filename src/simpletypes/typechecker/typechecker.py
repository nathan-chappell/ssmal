from typing import cast

from dataclasses import dataclass
import simpletypes.simple_ast.simple_ast_nodes as N


class TypeError(Exception):
    ...


@dataclass
class InheritanceGraphNode:
    name: N.TypeName
    base: "None | InheritanceGraphNode" = None

    def is_subtype_of(self, other_type_name: N.TypeName) -> bool:
        if self.name == other_type_name:
            return True
        base = self.base
        while base is not None:
            if base.name == other_type_name:
                return True
            base = base.base
        return False


_int = N.TypeName("int")
_str = N.TypeName("str")


class TypeChecker:
    identifiers: dict[N.Identifier, N.TypeName | N.FunctionDef]
    classes: dict[N.TypeName, InheritanceGraphNode]

    def __init__(self) -> None:
        self.identifiers = {}

        # "Builtin types"
        self.classes = {_int: InheritanceGraphNode(_int), _str: InheritanceGraphNode(_str)}

    def is_subtype_of(self, type: N.TypeName | N.FunctionDef, super_type: N.TypeName | N.FunctionDef) -> bool:
        match [type, super_type]:
            case [str(_type), str(_super_type)]:
                return self.classes[cast(N.TypeName, _type)].is_subtype_of(cast(N.TypeName, _super_type))
            case [
                N.FunctionDef(parameter_types=_parameter_types, return_type=_return_type),
                N.FunctionDef(parameter_types=_super_parameter_types, return_type=_super_return_type),
            ]:
                return (
                    len(_parameter_types) == len(_super_parameter_types)
                    and self.classes[_return_type].is_subtype_of(_super_return_type)
                    and all(
                        [
                            self.classes[_parameter_type].is_subtype_of(_super_parameter_type)
                            for _parameter_type, _super_parameter_type in zip(_parameter_types, _super_parameter_types)
                        ]
                    )
                )
            case _:
                return False

    def get_type(self, expression: N.Expression) -> N.TypeName | N.FunctionDef:
        match expression:
            case N.IdentifierExpr(identifier=identifier) if identifier not in self.identifiers:
                raise TypeError(f"Uknown {identifier=}", expression)
            case N.IdentifierExpr(identifier=identifier) if identifier in self.identifiers:
                return self.identifiers[identifier]

            case N.ValueExpr(value=int()):
                return _int
            case N.ValueExpr(value=str()):
                return _str
            case N.ValueExpr():
                raise TypeError(f"Uknown value type: {type(expression.value)}", expression)

            case N.CallExpr(function_name=function_name) if function_name not in self.identifiers:
                raise TypeError(f"Uknown function: {function_name}", expression)
            case N.CallExpr(function_name=function_name, arguments=arguments):
                function_def = self.identifiers[function_name]
                match function_def:
                    case str():
                        raise TypeError(f"Attempted to call variable: {function_name}", expression)
                    case N.FunctionDef(parameter_types=parameter_types, return_type=return_type):
                        argument_types = [self.get_type(argument) for argument in arguments]
                        for argument_type, parameter_type in zip(argument_types, parameter_types):
                            if not self.is_subtype_of(argument_type, parameter_type):
                                raise TypeError(f"Invalid call: {argument_type=} is not a subtype of {parameter_type=}", expression)
                        else:
                            return return_type
            case _:
                raise TypeError(f"Failed to evaluate expression.", expression)

    def check(self, program: N.Program):
        for statement in program.statements:
            match statement:
                case N.VariableDef(name=name) if name in self.identifiers:
                    raise TypeError(f"Variable {name} already defined.", statement)
                case N.VariableDef(name=name, type=type):
                    self.identifiers[name] = type

                case N.AssignmentStmt(target_variable=target_variable) if target_variable not in self.identifiers:
                    raise TypeError(f"Variable {statement.target_variable} not defined.", statement)
                case N.AssignmentStmt(target_variable=target_variable, value=value):
                    lhs = self.identifiers[target_variable]
                    rhs = self.get_type(value)
                    # check
                    if not self.is_subtype_of(lhs, rhs):
                        raise TypeError(f"Invalid assignment: {lhs} = {rhs}", statement)

                case N.ClassDef(base=base) if base is not None and base not in self.classes:
                    raise TypeError(f"Base class {base} not defined.", statement)
                case N.ClassDef(name=name) if name in self.classes:
                    raise TypeError(f"Class {name} already defined.", statement)
                case N.ClassDef(name=name, base=base):
                    base_node = self.classes.get(base) if base is not None else None
                    self.classes[name] = InheritanceGraphNode(name, base_node)

                case N.FunctionDef(name=name) if statement.name in self.identifiers:
                    raise TypeError(f"Variable {statement.name} already defined.", statement)
                case N.FunctionDef(name=name):
                    self.identifiers[name] = statement
        return True
