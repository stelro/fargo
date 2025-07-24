#!/usr/bin/env pwsh
<#
.SYNOPSIS
    fargo installer for Windows PowerShell

.DESCRIPTION
    Cross-platform installer for fargo C++ project manager.
    Supports both PowerShell Core and Windows PowerShell.

.PARAMETER User
    Install to user directory instead of system-wide

.PARAMETER Check
    Check system requirements only

.EXAMPLE
    .\install.ps1
    Install system-wide (requires Administrator)

.EXAMPLE
    .\install.ps1 -User
    Install to user directory

.EXAMPLE
    .\install.ps1 -Check
    Check system requirements only
#>

param(
    [switch]$User,
    [switch]$Check
)

# Color output functions
function Write-Info($message) {
    Write-Host "[install] $message" -ForegroundColor Blue
}

function Write-Success($message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "[ERROR] $message" -ForegroundColor Red
}

# Main installation logic
try {
    Write-Info "Installing fargo for Windows..."

    # Check if Python is available
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python not found"
        }
        Write-Info "Found Python: $pythonVersion"
    }
    catch {
        Write-Error "Python not found. Please install Python 3.7+ from https://python.org"
        Write-Error "Make sure to check 'Add Python to PATH' during installation"
        exit 1
    }

    # Check if fargo.py exists
    if (-not (Test-Path "fargo.py")) {
        Write-Error "fargo.py not found in current directory"
        exit 1
    }

    # Build arguments for Python installer
    $args = @("install.py")
    
    if ($User) {
        $args += "--user"
        Write-Info "Installing to user directory..."
    }
    elseif ($Check) {
        $args += "--check"
        Write-Info "Checking system requirements..."
    }
    else {
        Write-Info "Installing system-wide (requires Administrator)..."
    }

    # Run the Python installer
    $process = Start-Process -FilePath "python" -ArgumentList $args -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -ne 0) {
        Write-Error "Installation failed with exit code $($process.ExitCode)"
        exit $process.ExitCode
    }

    if (-not $Check) {
        Write-Success "Installation completed successfully!"
        Write-Host ""
        Write-Host "Try it out:"
        Write-Host "  fargo new myproject"
        Write-Host "  cd myproject"
        Write-Host "  fargo build"
    }
}
catch {
    Write-Error "Installation failed: $_"
    exit 1
}
