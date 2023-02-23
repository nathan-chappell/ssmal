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

# . .\Scripts\Activate.ps1

$Commands = @(
    @{ 
        Command = 'black --check .';
        Module  = 'black';
        Message = "Formatting failed.  Run 'black .' to fix." 
    }
    @{ 
        Command = 'pyright';
        Module  = 'pyright';
        Message = 'Type checking failed.  Fix all issues and re-run command.' 
    }
    @{ 
        Command = 'pytest';
        Module  = 'pytest';
        Message = 'Regression tests failed.  Fix all issues and re-run command.' 
    }
)

$Commands | ForEach-Object {
    python -c "import $($_.Module)"
    if ($LASTEXITCODE -ne 0) {
        "Module import failed for: $($_.Module).  Check your environment and install requirements.txt."
    }
    
    Invoke-Expression $_.Command
    if ($LASTEXITCODE -ne 0) {
        $_.Message | Write-Error
        exit 1
    }
}

function Bannerfy([string[]] $lines) {
    $lines | Measure-Object -Property Length -Maximum | Set-Variable 'stats'
    $leftSide = '*'
    $rightSide = '*'
    $padding = 2
    $topAndBottom = '*' * ($stats.Maximum + $leftSide.Length + $rightSide.Length + 2 * $padding)

    $topAndBottom | Write-Host -BackgroundColor Blue -NoNewline
    '' | Write-Host -BackgroundColor Black

    $lines | ForEach-Object {
        $leftSide | Write-Host -BackgroundColor Blue -NoNewline
        ' ' * $padding | Write-Host -BackgroundColor Black -NoNewline
        $_ | Write-Host -BackgroundColor Black -NoNewline
        ' ' * ($stats.Maximum - $_.Length) | Write-Host -BackgroundColor Black -NoNewline
        ' ' * $padding | Write-Host -BackgroundColor Black -NoNewline
        $rightSide | Write-Host -BackgroundColor Blue -NoNewline
        '' | Write-Host -BackgroundColor Black
    }

    $topAndBottom | Write-Host -BackgroundColor Blue -NoNewline
    '' | Write-Host -BackgroundColor Black
}

$successMessage = 'dev-pipline completed successfully!', "Have a `u{1f32e}"

Bannerfy $successMessage

# $successMessage = "dev-pipline completed successfully! Have a `u{1f32e}"

# '*'*40 | Write-Host -BackgroundColor Blue
# '*' | Write-Host -BackgroundColor Blue -NoNewline
# " $successMessage " | Write-Host -BackgroundColor Black -NoNewline
# '*' | Write-Host -BackgroundColor Blue
# '*'*40 | Write-Host -BackgroundColor Blue
