# User-run Windows bootstrap: real VS Code extensions, Python venv and Jupyter tests.
# -VerifyOnly performs read-only checks; no installs and no report writes.
param(
    [ValidateSet("smoke", "all")]
    [string]$Mode = "smoke",
    [switch]$VerifyOnly
)
$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $root
try {
    $python = $null
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $python = @("py", "-3")
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $python = @("python")
    }
    if (-not $python) {
        Write-Error "Install Python 3.11+ to complete the setup."
        exit 2
    }

    if (-not $VerifyOnly) {
        & $python[0] @($python[1..($python.Count - 1)]) -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 2)"
        if ($LASTEXITCODE -ne 0) { throw "Python 3.11+ is required." }
        & powershell -NoProfile -File "$root\scripts\install-vscode-extensions.ps1"
        if ($LASTEXITCODE -ne 0) { throw "VS Code extension installation failed." }
        if (-not (Test-Path ".venv\Scripts\python.exe")) {
            & $python[0] @($python[1..($python.Count - 1)]) -m venv .venv
            if ($LASTEXITCODE -ne 0) { throw "Could not create the Python virtual environment." }
        }
        & ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -r notebooks\requirements-vscode.txt
        if ($LASTEXITCODE -ne 0) { throw "Could not install notebook dependencies." }
    } else {
        & powershell -NoProfile -File "$root\scripts\install-vscode-extensions.ps1" -VerifyOnly
        if ($LASTEXITCODE -ne 0) { throw "Required extensions are not installed." }
        if (-not (Test-Path ".venv\Scripts\python.exe")) {
            throw "Missing .venv — run the setup task first."
        }
    }

    $venvPython = ".venv\Scripts\python.exe"
    $verifyArgs = @("scripts\verify_learning_environment.py", "--mode", $Mode)
    if (-not $VerifyOnly) { $verifyArgs += "--write-report" }
    & $venvPython @verifyArgs
    if ($LASTEXITCODE -ne 0) { throw "Jupyter/Markdown readiness check failed." }

    foreach ($script in @("scripts\validate_repo.py", "scripts\audit_program.py", "scripts\check_english_content.py")) {
        & $venvPython $script
        if ($LASTEXITCODE -ne 0) { throw "Local CI check failed: $script" }
    }
    & $venvPython -m unittest discover -s tests -q
    if ($LASTEXITCODE -ne 0) { throw "Local unit tests failed." }

    Write-Host "PASS: local course setup and CI checks finished successfully."
    if (-not $VerifyOnly) {
        Write-Host "Sanitized results saved to learner/setup-check.local.json (gitignored)."
    }
} finally {
    Pop-Location
}
