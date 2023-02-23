# .SYNOPSIS
#
# Runs standard tools for project.
# Should be run from the project root prior to submitting a pull request.
#
# .DESCRIPTION
#
# The "dev-pipeline" consists of running:
# 1. black .
# 2. pyright
# 3. pytest tests
#
# These same commands will be run on the build-server, so if they fail locally then your PR certainly will be rejected.
#
# NOTE:
# "Failing" the `black` command just means that black ran and some file was reformatted.


function GetInspirationalMessage {
    switch (Get-Random -Maximum 2)
    {
        0 { "Have a `u{1f32e}" }
        1 { "It's a bright, shiny day!" }
    }
}

function Bannerfy([string[]] $lines, [string]$bgColor) {
    $_lines = $lines, '', (GetInspirationalMessage) | % { $_ }
    $_lines | Measure-Object -Property Length -Maximum | Set-Variable 'stats'
    $leftSide = '*'
    $rightSide = '*'
    $padding = 2
    $topAndBottom = '*' * ($stats.Maximum + $leftSide.Length + $rightSide.Length + 2 * $padding)

    function _write([string]$line, [switch]$bg) { 
        $_params = if ($bg) { @{BackgroundColor = $bgColor } } else { @{} }
        $line | Write-Host @_params -NoNewline 
    }
    function _newLine { '' | Write-Host -BackgroundColor Black }

    $_padding = ' ' * $padding
    _write $topAndBottom -bg
    _newLine

    $_lines | ForEach-Object {
        $_spacing = ' ' * ($stats.Maximum - $_.Length)
        _write $leftSide
        _write $_padding
        _write $_
        _write $_spacing
        _write $_padding
        _write $leftSide
        _newLine
    }
    
    _write $topAndBottom -bg
    _newLine
}

$Commands = @(
    @{ 
        Command = 'black --check .';
        Module  = 'black';
        Message = 'Formatting failed.', "Run 'black .' to fix.";
    }
    @{ 
        Command = 'pyright';
        Module  = 'pyright';
        Message = 'Type checking failed.', 'Fix all issues and re-run command.';
    }
    @{ 
        Command = 'pytest';
        Module  = 'pytest';
        Message = 'Regression tests failed.', 'Fix all issues and re-run command.';
    }
)

$Commands | ForEach-Object {
    python -c "import $($_.Module)"
    if ($LASTEXITCODE -ne 0) {
        $moduleImportFailMessage = (
            "Module import failed for: $($_.Module).",
            'Check your environment (default interpreter),',
            'and install requirements.txt:',
            '       >',
            '       > . .\Scripts\Activate.ps1',
            '(ssmal)> pip install -r requirements.txt',
            '       >'
        )
        Bannerfy $moduleImportFailMessage -bgColor "DarkYellow"
        exit 1
    }
    
    Invoke-Expression $_.Command
    if ($LASTEXITCODE -ne 0) {
        Bannerfy $_.Message -bgColor "Red"
        exit 1
    }
}

$successMessage = 'dev-pipline completed successfully!'

Bannerfy $successMessage -bgColor "Green"