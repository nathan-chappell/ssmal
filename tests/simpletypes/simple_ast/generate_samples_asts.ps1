
$output = '.\tests\simpletypes\simple_ast\samples_asts_generated.py'

@'
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

'@ > $output

$sampleNames = gci .\tests\simpletypes\samples | % { $_.FullName -replace '\\', '/' -replace '.*/tests', 'tests' }

$sampleNames | % {
    $shortName = $_ -replace '.*/','' -replace '.py',''
    '# ' + $_; 
    '';
    $shortName + '_expected = ' + (python -m simpletypes -p $_) -creplace "('[a-z]\')", '_I($1)' -creplace "(?!_I)'(str|int|[A-Z]\w*)'", '_T(''$1'')' 
} >> $output

@'
@pytest.mark.parametrize(
    "filename,expected",
    [
'@ >> $output

$sampleNames | %{
    $shortName = $_ -replace '.*/','' -replace '.py',''
"        ('$_', $($shortName)_expected),"
} >> $output

@'
    ],
)
def test_simple_ast_parser(filename: str, expected: Program):
    with open(filename) as f:
        text = f.read()
    module = ast.parse(text)
    program = parse_Program(module)
    assert program == expected
'@ >> $output

Invoke-Expression "black $output"