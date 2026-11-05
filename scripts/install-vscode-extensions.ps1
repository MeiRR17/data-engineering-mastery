# User-initiated Visual Studio Code extension setup for Windows PowerShell.
# This script changes only installed VS Code extensions in the current user profile.
# No repository files, environment variables, cloud resources or secrets are modified.
$ErrorActionPreference = "Stop"

$extensions = @(
    "ms-python.python",
    "ms-toolsai.jupyter",
    "yzhang.markdown-all-in-one",
    "shd101wyy.markdown-preview-enhanced"
)

$code = Get-Command code -ErrorAction SilentlyContinue
if (-not $code) {
    Write-Error @'
The Visual Studio Code "code" command is not on PATH.
Open VS Code -> Extensions (Ctrl+Shift+X), and install:
  Python (Microsoft), Jupyter (Microsoft),
  Markdown All in One, Markdown Preview Enhanced.
You can also install VS Code so its command-line launcher is on PATH.
'@
    exit 2
}

foreach ($extension in $extensions) {
    Write-Host "Installing VS Code extension: $extension"
    & $code.Source --install-extension $extension
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Extension installation failed: $extension (exit $LASTEXITCODE)"
        exit 1
    }
}

$installed = & $code.Source --list-extensions
if ($LASTEXITCODE -ne 0) {
    Write-Error "Cannot verify installed VS Code extensions."
    exit 1
}
$missing = @($extensions | Where-Object { $installed -notcontains $_ })
if ($missing.Count -gt 0) {
    Write-Error ("Could not verify installed extensions: " + ($missing -join ", "))
    exit 1
}
Write-Host "PASS: All four extensions are listed as installed in this VS Code profile."
Write-Host "Open the repository as a folder. Preview .md with Ctrl+Shift+V."
Write-Host "Open .ipynb using 'Reopen Editor With... -> Jupyter Notebook' if needed."
