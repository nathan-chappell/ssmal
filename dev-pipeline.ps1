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
    switch (Get-Random -Maximum 2) {
        0 { "Have a `u{1f32e}" }
        1 { "`u{1f31e} It's a bright, shiny day! `u{1f31e}" }
    }
}

function Bannerfy([string[]] $lines, [string]$bgColor, [switch]$inspire) {
    if ($inspire) {
        $_lines = $lines, '', (GetInspirationalMessage) | % { $_ }
    }
    else {
        $_lines = $lines
    }
    $_lines | Measure-Object -Property Length -Maximum | Set-Variable 'stats'
    $side = '#'
    $padding = 2
    $topAndBottom = '#' * ($stats.Maximum + 2 * ($side.Length + $padding))

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
        _write $side -bg
        _write $_padding
        _write $_
        _write $_spacing
        _write $_padding
        _write $side -bg
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

class MissingTestInfo {
    [string] $FileName
    [int[]] $LineNumbers

    MissingTestInfo([string] $FileName, [int[]] $LineNumbers) {
        $this.FileName = $FileName
        $this.LineNumbers = $LineNumbers
    }

    [string[]] GetMissingLines() {
        $content = Get-Content $_.FileName
        return $this.LineNumbers | % {
            $_.ToString('D3') + ': ' + $content[$_ - 1]
        }
    }
}

function GetMissingTestInfo {
    [OutputType([MissingTestInfo[]])]
    param (
        [string]$coverageFileName = 'coverage.xml'
    )
    Select-Xml '//class' .\coverage.xml | ? {
        $_.Node.SelectNodes('.//line[@hits="0"]').Count -gt 0
    } | % {
        $lineNumbers = $_.Node.SelectNodes('lines/line[@hits="0"]') | % { [int]::Parse($_.number) }
        [MissingTestInfo]::new($_.Node.filename, $lineNumbers)
    }
}

function CheckTestCoverage([string[]]$fileNames = @()) {
    [MissingTestInfo[]]$missingTestInfo = GetMissingTestInfo
    if ($fileNames.Count -gt 0) {
        $missingTestInfo = $missingTestInfo | ? { 
            $info = $_; 
            $fileNames | % { if ($info.FileName.Contains($_)) { $true } } 
        }
    }
    $failedCoverage = $missingTestInfo.Count -gt 0

    if ($failedCoverage) {
        $missingTestInfo | % {
            Bannerfy @('Missing tests for', $_.FileName) -bgColor 'Red'
            $_.GetMissingLines() | % {
                $_ | Write-Host
            }
        }
        Bannerfy 'Please cover your code with tests.' -bgColor Cyan -inspire
        return $false
    }
    return $true
}

function DevPipeline() {
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
            Bannerfy $moduleImportFailMessage -bgColor 'DarkYellow' -inspire
            exit 1
        }
        
        Invoke-Expression $_.Command
        if ($LASTEXITCODE -ne 0) {
            Bannerfy $_.Message -bgColor 'Red' -inspire
            exit 1
        }
    }

    if (CheckTestCoverage) {
        $successMessage = 'dev-pipline completed successfully!'
        Bannerfy $successMessage -bgColor 'Green' -inspire
    } else {
        exit 1
    }
}


if ($MyInvocation.InvocationName -ne '.') {
    DevPipeline
}