
$output = '.\tests\simpletypes\simple_ast\samples_asts_generated.py'

@'
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

'@ > $output

gci .\tests\simpletypes\samples\ | % {
    '# ' + $_.FullName; 
    '';
    $_.Name.Replace('.py', '_expected = ') + (python -m simpletypes -p $_.FullName) -creplace "('[a-z]\')", '_I($1)' -creplace "(?!_I)'(str|int|[A-Z]\w*)'", '_T(''$1'')' 
} >> $output

Invoke-Expression "black $output"