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

from tests.simpletypes.simple_ast.samples_asts_generated import (
    classes_expected,
    expressions_expected,
    functions_expected,
    variables_expected,
)


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("tests/simpletypes/samples/classes.py", classes_expected),
        ("tests/simpletypes/samples/functions.py", functions_expected),
        ("tests/simpletypes/samples/variables.py", variables_expected),
        ("tests/simpletypes/samples/expressions.py", expressions_expected),
    ],
)
def test_simple_ast_parser(filename: str, expected: Program):
    with open(filename) as f:
        text = f.read()
    module = ast.parse(text)
    program = parse_Program(module)
    assert program == expected
