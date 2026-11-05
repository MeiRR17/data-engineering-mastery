# Opt-in installer/verification for Windows VS Code CLI.
# This does not change the system execution policy, Git credentials or cloud state.
param([switch]$VerifyOnly)

$ErrorActionPreference = "Stop"
$extensions = @(
    "ms-python.python",
    "ms-toolsai.jupyter",
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced"
)

$cli = $null
if ($env:VSCODE_CLI -and (Test-Path -LiteralPath $env:VSCODE_CLI -PathType Leaf)) {
    $cli = $env:VSCODE_CLI
} else {
    $command = Get-Command code -ErrorAction SilentlyContinue
    if ($command) { $cli = $command.Source }
    if (-not $cli) {
        $candidates = @(
            (Join-Path $env:LOCALAPPDATA "Programs\Microsoft VS Code\bin\code.cmd"),
            (Join-Path $env:ProgramFiles "Microsoft VS Code\bin\code.cmd")
        )
        foreach ($candidate in $candidates) {
            if (Test-Path -LiteralPath $candidate -PathType Leaf) {
                $cli = $candidate
                break
            }
        }
    }
}
if (-not $cli) {
    Write-Error "VS Code CLI not found. Use the Extensions sidebar to install Python, Jupyter, Markdown All in One, and Markdown Preview Enhanced, or add the official code launcher to PATH."
    exit 2
}

& $cli --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "VS Code CLI could not start."
    exit 2
}

if (-not $VerifyOnly) {
    foreach ($extension in $extensions) {
        Write-Host "Installing/refreshing extension: $extension"
        & $cli --install-extension $extension
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Installation failed: $extension"
            exit 1
        }
    }
}

$installed = @(& $cli --list-extensions --show-versions)
if ($LASTEXITCODE -ne 0) {
    Write-Error "VS Code could not list extensions."
    exit 1
}
$installedNames = @($installed | ForEach-Object {
    (($_.ToString().Trim() -split "@", 2)[0]).ToLowerInvariant()
})
$missing = @($extensions | Where-Object { $installedNames -notcontains $_ })
if ($missing.Count -ne 0) {
    Write-Error ("Extensions missing from this VS Code profile: " + ($missing -join ", "))
    exit 1
}
foreach ($extension in $extensions) { Write-Host "PASS: installed $extension" }
Write-Host "PASS: four extensions verified in the VS Code CLI context checked."
