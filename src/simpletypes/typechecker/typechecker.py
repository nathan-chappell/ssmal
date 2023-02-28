import simpletypes.simple_ast.simple_ast_nodes as N


class TypeError(Exception):
    ...


class TypeChecker:
    context: dict[N.Identifier, N.TypeName]
    functions: dict[N.Identifier, N.FunctionDef]
    subclasses: dict[N.TypeName, set[N.TypeName]]

    def __init__(self) -> None:
        self.context = {}
        self.functions = {}
        self.subclasses = dict()

    def get_type(self, expression: N.Expression) -> N.TypeName:
        ...

    def check(self, program: N.Program):
        for statement in program.statements:
            match (statement):
                case N.VariableDef():
                    if statement.name in self.context:
                        raise TypeError(f"Variable {statement.name} already defined.", statement)
                    else:
                        self.context[statement.name] = statement.type
                case N.AssignmentStmt():
                    if statement.target_variable not in self.context:
                        raise TypeError(f"Variable {statement.target_variable} not defined.", statement)
                    else:
                        lhs = self.context[statement.target_variable]
                        rhs = self.get_type(statement.value)
                        if lhs not in self.subclasses[rhs]:
                            raise TypeError(f"Invalid assignment: {lhs} = {rhs}", statement)
                case N.ClassDef():
                    base = statement.base
                    name = statement.name
                    if base is not None and base not in self.subclasses:
                        raise TypeError(f"Base class {base} not defined.", statement)
                    if name in self.subclasses:
                        raise TypeError(f"Class {name} already defined.", statement)
                    self.subclasses[name] = set([name])
                    while base is not None:
                        self.subclasses[base].add(name)
                case N.FunctionDef():
                    if statement.name in self.context:
                        raise TypeError(f"Variable {statement.name} already defined.", statement)
                    self.functions[statement.name] = statement
