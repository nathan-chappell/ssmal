
$output = '.\tests\ssmal\lang\tm\generated_parser_test.py'

@'
import pytest

from ssmal.lang.tm.parser import parse_binary_transitions, BinaryTransition, TmParseError

'@ > $output

$sampleNames = gci .\tests\ssmal\lang\tm\samples | % { $_.FullName -replace '\\', '/' -replace '.*/tests', 'tests' }

function GetShortName([string]$name) {
    $name -replace '.*/','' -replace '.tm',''
}

$sampleNames | % {
    $shortName = GetShortName $_
    '# ' + $_; 
    '';
    $shortName + '_expected = ' + (python .\src\ssmal\lang\tm\parser.py $_)
} >> $output

@'
@pytest.mark.parametrize(
    "filename,expected",
    [
'@ >> $output

$sampleNames | %{
    $shortName = GetShortName $_
"        ('$_', $($shortName)_expected),"
} >> $output

@'
    ],
)
def test_simple_ast_parser(filename: str, expected: list[BinaryTransition]):
    with open(filename) as f:
        text = f.read()
    binary_transitions = list(parse_binary_transitions(text))
    assert binary_transitions == expected
'@ >> $output

Invoke-Expression "black $output"