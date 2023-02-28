import pytest

import simpletypes.simple_ast.simple_ast_nodes as N
from simpletypes.simple_ast.simple_ast_parser import parse
from simpletypes.typechecker.typechecker import TypeChecker


_int = N.TypeName("int")
_str = N.TypeName("str")


@pytest.mark.parametrize(
    "filename",
    [
        ("tests/simpletypes/samples/classes.py"),
        ("tests/simpletypes/samples/expressions.py"),
        ("tests/simpletypes/samples/functions.py"),
        ("tests/simpletypes/samples/subtyping_1.py"),
        ("tests/simpletypes/samples/variables.py"),
    ],
)
def test_typechecker_valid_samples(filename: str):
    type_checker = TypeChecker()
    with open(filename) as f:
        program = parse(f.read())
        type_checker.check(program)


def test_typechecker_is_subtype_of_builtins():
    type_checker = TypeChecker()
    assert not type_checker.is_subtype_of(_int, _str)
    assert not type_checker.is_subtype_of(_str, _int)


def test_typechecker_is_subtype_of_functions():
    type_checker = TypeChecker()

    filename = "tests/simpletypes/samples/classes.py"
    with open(filename) as f:
        program = parse(f.read())
        type_checker.check(program)

    _B = N.TypeName("B")
    _D = N.TypeName("D")
    _DD = N.TypeName("DD")
    _f = N.Identifier("f")

    f = N.FunctionDef(_f, [_D], _D)
    f_cov = N.FunctionDef(_f, [_D], _DD)
    f_con = N.FunctionDef(_f, [_DD], _D)

    assert type_checker.is_subtype_of(_D, _B)
    assert type_checker.is_subtype_of(_DD, _D)
    assert type_checker.is_subtype_of(_DD, _B)
    assert not type_checker.is_subtype_of(_B, _D)
    assert not type_checker.is_subtype_of(_B, _DD)

    assert type_checker.is_subtype_of(f_cov, f)
    assert type_checker.is_subtype_of(f_con, f)
    assert not type_checker.is_subtype_of(f_con, _B)
