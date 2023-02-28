import ast
import pytest

import simpletypes
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


_expected_classes = Program(statements=[ClassDef(name=_T("B")), ClassDef(name=_T("D"), base=_T("B"))])
_expected_functions = Program(
    statements=[
        FunctionDef(parameter_types=[_T("int")], return_type=_T("str")),
        FunctionDef(parameter_types=[_T("str"), _T("str")], return_type=_T("None")),
    ]
)
_expected_variables = Program(
    statements=[
        FunctionDef(parameter_types=[_T("int")], return_type=_T("str")),
        VariableDef(name=_I("x"), type=_T("int")),
        AssignmentStmt(target_variable=_I("x"), value=ValueExpr(value=0)),
        VariableDef(name=_I("y"), type=_T("str")),
        AssignmentStmt(target_variable=_I("y"), value=CallExpr(function_name=_I("f"), arguments=[IdentifierExpr(identifier=_I("x"))])),
    ]
)

_expected_expressions = Program(
    statements=[
        VariableDef(name=_I("x"), type=_T("int")),
        VariableDef(name=_I("y"), type=_T("str")),
        AssignmentStmt(target_variable=_I("x"), value=ValueExpr(value=0)),
        AssignmentStmt(target_variable=_I("y"), value=ValueExpr(value="foobar")),
        FunctionDef(parameter_types=[_T("int"), _T("str")], return_type=_T("str")),
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


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("tests/simpletypes/samples/classes.py", _expected_classes),
        ("tests/simpletypes/samples/functions.py", _expected_functions),
        ("tests/simpletypes/samples/variables.py", _expected_variables),
        ("tests/simpletypes/samples/expressions.py", _expected_expressions),
    ],
)
def test_simple_ast_parser(filename: str, expected: Program):
    with open(filename) as f:
        text = f.read()
    module = ast.parse(text)
    program = parse_Program(module)
    assert program == expected
