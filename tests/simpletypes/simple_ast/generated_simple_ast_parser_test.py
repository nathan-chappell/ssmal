import ast

import pytest

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

from simpletypes.simple_ast.simple_ast_parser import parse_Program

_I = Identifier
_T = TypeName

# tests/simpletypes/samples/classes.py

classes_expected = Program(
    statements=[ClassDef(name=_T("B"), base=None), ClassDef(name=_T("D"), base=_T("B")), ClassDef(name=_T("DD"), base=_T("D"))]
)
# tests/simpletypes/samples/expressions.py

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
# tests/simpletypes/samples/functions.py

functions_expected = Program(
    statements=[
        FunctionDef(name=_I("f"), parameter_types=[_T("int")], return_type=_T("str")),
        FunctionDef(name=_I("g"), parameter_types=[_T("str"), _T("str")], return_type=_T("None")),
    ]
)
# tests/simpletypes/samples/subtyping_1.py

subtyping_1_expected = Program(
    statements=[
        ClassDef(name=_T("B"), base=None),
        ClassDef(name=_T("D"), base=_T("B")),
        ClassDef(name=_T("DD"), base=_T("D")),
        VariableDef(name=_I("b"), type=_T("B")),
        VariableDef(name=_I("d"), type=_T("DD")),
        VariableDef(name=_I("x"), type=_T("int")),
        FunctionDef(name=_I("f"), parameter_types=[_T("B"), _T("D")], return_type=_T("int")),
        AssignmentStmt(target_variable=_I("b"), value=IdentifierExpr(identifier=_I("d"))),
        AssignmentStmt(
            target_variable=_I("x"),
            value=CallExpr(function_name=_I("f"), arguments=[IdentifierExpr(identifier=_I("d")), IdentifierExpr(identifier=_I("d"))]),
        ),
    ]
)
# tests/simpletypes/samples/variables.py

variables_expected = Program(
    statements=[
        FunctionDef(name=_I("f"), parameter_types=[_T("int")], return_type=_T("str")),
        VariableDef(name=_I("x"), type=_T("int")),
        AssignmentStmt(target_variable=_I("x"), value=ValueExpr(value=0)),
        VariableDef(name=_I("y"), type=_T("str")),
        AssignmentStmt(target_variable=_I("y"), value=CallExpr(function_name=_I("f"), arguments=[IdentifierExpr(identifier=_I("x"))])),
    ]
)


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("tests/simpletypes/samples/classes.py", classes_expected),
        ("tests/simpletypes/samples/expressions.py", expressions_expected),
        ("tests/simpletypes/samples/functions.py", functions_expected),
        ("tests/simpletypes/samples/subtyping_1.py", subtyping_1_expected),
        ("tests/simpletypes/samples/variables.py", variables_expected),
    ],
)
def test_simple_ast_parser(filename: str, expected: Program):
    with open(filename) as f:
        text = f.read()
    module = ast.parse(text)
    program = parse_Program(module)
    assert program == expected
