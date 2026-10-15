[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$SetupScript = Join-Path $Root "setup-hermes.ps1"
$DependencyGate = Join-Path $PSScriptRoot "oneclick_dependency_gate.ps1"
$InstallScript = Join-Path $Root "workstation\install.ps1"
$DoctorScript = Join-Path $Root "workstation\doctor.ps1"
$StartScript = Join-Path $Root "workstation\start.ps1"

$RuntimeRoot = if ($env:HERMES_WORKSTATION_HOME -and $env:HERMES_WORKSTATION_HOME.Trim()) {
  [System.IO.Path]::GetFullPath($env:HERMES_WORKSTATION_HOME.Trim())
} elseif ($env:LOCALAPPDATA) {
  Join-Path $env:LOCALAPPDATA "HermesWorkstation"
} else {
  Join-Path $HOME ".hermes-workstation"
}
$UpstreamStamp = Join-Path $RuntimeRoot "Runtime\oneclick-upstream-inputs.sha256"

function Get-UpstreamFingerprint {
  # The upstream PM owns its tools and Python dependency graph.
  $inputs = @(
    "pm\lock.json", "pyproject.toml", "uv.lock", ".python-version",
    ".nvmrc", "setup-hermes.ps1", "pm\cli.py", "pm\environments.py",
    "workstation\scripts\oneclick_bootstrap.ps1"
  )
  $parts = New-Object System.Collections.Generic.List[string]
  foreach ($relative in $inputs) {
    $file = Join-Path $Root $relative
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
      throw "Required upstream bootstrap input is missing: $relative"
    }
    $parts.Add("$relative=$((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash)")
  }
  $bytes = [Text.Encoding]::UTF8.GetBytes(($parts -join [char]10))
  $sha = [Security.Cryptography.SHA256]::Create()
  try { return [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace("-", "") }
  finally { $sha.Dispose() }
}

function Test-Python314 {
  param([string]$Path)
  if (-not $Path -or -not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
  try {
    $output = & $Path -I -c "import sys; print('ok' if sys.version_info[:2] == (3,14) else 'bad')" 2>$null
    return ($LASTEXITCODE -eq 0 -and ($output | Select-Object -Last 1) -eq "ok")
  } catch { return $false }
}

function Find-PmPython {
  # A committed PM interpreter takes precedence over a global Python alias.
  foreach ($candidate in @(
    (Join-Path $Root "venv\Scripts\python.exe"),
    (Join-Path $Root ".venv\Scripts\python.exe")
  )) {
    if (Test-Python314 $candidate) { return $candidate }
  }

  # The upstream setup stages SHA-pinned uv and a managed Python.
  $lock = Get-Content -LiteralPath (Join-Path $Root "pm\lock.json") -Raw | ConvertFrom-Json
  $nativeArch = if ($env:PROCESSOR_ARCHITEW6432) { $env:PROCESSOR_ARCHITEW6432 } else { $env:PROCESSOR_ARCHITECTURE }
  $arch = if ($nativeArch -eq "ARM64") { "arm64" } else { "x64" }
  $target = "win32-$arch"
  $store = if ($env:HERMES_RUNTIME_DIR) { $env:HERMES_RUNTIME_DIR } else { Join-Path $HOME ".hermes\tools" }
  $uv = Join-Path $store "uv-$($lock.packages.uv.version)-$target\uv.exe"
  if (-not (Test-Path -LiteralPath $uv -PathType Leaf)) { return $null }
  $pyVersion = [string]$lock.packages.python.version
  $pyMinor = ($pyVersion -split "\+")[0] -replace "^(\d+\.\d+).*", '$1'
  $triple = if ($arch -eq "arm64") { "aarch64" } else { "x86_64" }
  try {
    $resolved = & $uv python find --managed-python "cpython-$pyMinor-windows-$triple-none" 2>$null
    if ($LASTEXITCODE -ne 0) { return $null }
    $path = ([string]($resolved | Select-Object -Last 1)).Trim()
    if (Test-Python314 $path) { return $path }
  } catch { }
  return $null
}

function Enter-UpstreamEnvironment {
  $python = Find-PmPython
  if (-not $python) { return $false }
  try {
    # Use upstream's own PATH composer; do not write global PATH or registry.
    $json = & $python -m pm.environments 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $json) { return $false }
    $composed = ($json -join [char]10) | ConvertFrom-Json
    foreach ($property in $composed.PSObject.Properties) {
      if ($null -ne $property.Value) {
        [Environment]::SetEnvironmentVariable($property.Name, [string]$property.Value, "Process")
      }
    }
    $env:HERMES_PYTHON = $python
    # -I would discard the composed PYTHONPATH and falsely reject healthy PM
    # generations. Probe real pinned runtime dependencies, not just sources.
    $pyCheck = & $python -c "import hermes_cli, httpx, pydantic; from importlib.metadata import version; version('hermes-agent'); print('ok')" 2>$null
    if ($LASTEXITCODE -ne 0 -or ($pyCheck | Select-Object -Last 1) -ne "ok") { return $false }
    if (-not (Get-Command node -ErrorAction SilentlyContinue) -or
        -not (Get-Command npm -ErrorAction SilentlyContinue) -or
        -not (Get-Command git -ErrorAction SilentlyContinue)) { return $false }
    $nodeOut = & node -p "process.versions.node" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $nodeOut) { return $false }
    $nodeVersion = [version]([string]($nodeOut | Select-Object -Last 1))
    if ($nodeVersion -lt [version]"22.22.0") { return $false }
    $npmOut = & cmd.exe /d /c "npm --version 2>NUL"
    if ($LASTEXITCODE -ne 0 -or -not $npmOut) { return $false }
    $gitOut = & git --version 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $gitOut) { return $false }
    Write-Host "[bootstrap] Python 3.14, Node $nodeVersion, npm and Git ready." -ForegroundColor Green
    return $true
  } catch {
    Write-Host "[bootstrap] Existing upstream environment not usable: $($_.Exception.Message)" -ForegroundColor Yellow
    return $false
  }
}

function Invoke-Step {
  param([string]$Name, [string]$Script, [string[]]$Arguments = @())
  Write-Host ""
  Write-Host $Name -ForegroundColor Cyan
  # Child PowerShell isolates exit/terminating errors and forwards the exact
  # exit status without losing the parent's PM-composed process environment.
  & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $Script @Arguments
  if ($LASTEXITCODE -ne 0) { throw "$Name failed (exit code $LASTEXITCODE)." }
}

try {
  Push-Location -LiteralPath $Root
  try {
    Write-Host "============================================================"
    Write-Host " HERMES WORK - ONE-CLICK BOOTSTRAP"
    Write-Host "============================================================"
    $fingerprint = Get-UpstreamFingerprint
    $stampMatches = $false
    if (Test-Path -LiteralPath $UpstreamStamp -PathType Leaf) {
      try { $stampMatches = ([IO.File]::ReadAllText($UpstreamStamp).Trim() -eq $fingerprint) }
      catch { Write-Host "[bootstrap] Previous install record unreadable; repairing." -ForegroundColor Yellow }
    }
    if (-not $stampMatches -or -not (Enter-UpstreamEnvironment)) {
      Write-Host "[0/4] Installing or repairing pinned upstream tools and Python dependencies..." -ForegroundColor Cyan
      Write-Host "      First run requires internet to fetch SHA256-verified archives."
      # Official upstream package-management path, including optional defaults.
      # setup-hermes.ps1 explicitly calls exit 0 under -RuntimeOnly. Running
      # it in-process would terminate THIS launcher before Electron starts.
      & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $SetupScript -RuntimeOnly
      if ($LASTEXITCODE -ne 0) { throw "Upstream package manager failed (exit code $LASTEXITCODE)." }
      if (-not (Enter-UpstreamEnvironment)) {
        throw "Upstream setup returned without a usable Python 3.14 / Node / npm / Git environment."
      }
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $UpstreamStamp) | Out-Null
      [IO.File]::WriteAllText($UpstreamStamp, $fingerprint)
      Write-Host "[bootstrap] Upstream installation fingerprint recorded." -ForegroundColor Green
    } else {
      Write-Host "[0/4] Upstream dependencies unchanged and healthy; skipping install." -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "[1/4] Checking Workstation dependency fingerprint..." -ForegroundColor Cyan
    & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $DependencyGate -Action Check
    $needsInstall = ($LASTEXITCODE -ne 0)
    if ($needsInstall) {
      Invoke-Step -Name "[2/4] Installing missing/changed Workstation dependencies..." -Script $InstallScript
      Invoke-Step -Name "[deps] Recording completed Workstation install..." -Script $DependencyGate -Arguments @("-Action", "Record")
    } else {
      Invoke-Step -Name "[2/4] Validating existing Workstation install..." -Script $InstallScript -Arguments @("-SkipDependencies")
    }
    Invoke-Step -Name "[3/4] Running strict Workstation doctor..." -Script $DoctorScript -Arguments @("-Strict")
    Invoke-Step -Name "[4/4] Starting Hermes Work..." -Script $StartScript -Arguments @("-SkipInstall")
    exit 0
  } finally {
    Pop-Location
  }
} catch {
  Write-Host ""
  Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
  Write-Host "The existing environment was preserved. Review the error above and retry."
  exit 1
}
