from simpletypes.simple_ast.simple_ast_nodes import (
    AssignmentStmt,
    CallExpr,
    ClassDef,
    FunctionDef,
    Identifier,
    IdentifierExpr,
    Program,
    TypeName,
    ValueExpr,
    VariableDef,
)

_I = Identifier
_T = TypeName

# D:\programming\py\ssmal\tests\simpletypes\samples\classes.py

classes_expected = Program(statements=[ClassDef(name=_T("B"), base=None), ClassDef(name=_T("D"), base=_T("B"))])
# D:\programming\py\ssmal\tests\simpletypes\samples\expressions.py

expressions_expected = Program(
    statements=[
        VariableDef(name=_I("x"), type=_T("int")),
        VariableDef(name=_I("y"), type=_T("str")),
        AssignmentStmt(target_variable=_I("x"), value=ValueExpr(value=0)),
        AssignmentStmt(target_variable=_I("y"), value=ValueExpr(value="foobar")),
        FunctionDef(name=_I("f"), parameter_types=[_T("int"), _T("str")], return_type=_T("str")),
        AssignmentStmt(
            target_variable=_I("y"),
            value=CallExpr(
                function_name=_I("f"),
                arguments=[
                    IdentifierExpr(identifier=_I("x")),
                    CallExpr(function_name=_I("f"), arguments=[ValueExpr(value=123), IdentifierExpr(identifier=_I("y"))]),
                ],
            ),
        ),
    ]
)
# D:\programming\py\ssmal\tests\simpletypes\samples\functions.py

functions_expected = Program(
    statements=[
        FunctionDef(name=_I("f"), parameter_types=[_T("int")], return_type=_T("str")),
        FunctionDef(name=_I("g"), parameter_types=[_T("str"), _T("str")], return_type=_T("None")),
    ]
)
# D:\programming\py\ssmal\tests\simpletypes\samples\variables.py

variables_expected = Program(
    statements=[
        FunctionDef(name=_I("f"), parameter_types=[_T("int")], return_type=_T("str")),
        VariableDef(name=_I("x"), type=_T("int")),
        AssignmentStmt(target_variable=_I("x"), value=ValueExpr(value=0)),
        VariableDef(name=_I("y"), type=_T("str")),
        AssignmentStmt(target_variable=_I("y"), value=CallExpr(function_name=_I("f"), arguments=[IdentifierExpr(identifier=_I("x"))])),
    ]
)
