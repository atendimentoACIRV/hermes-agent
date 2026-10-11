[CmdletBinding()]
param(
  [ValidateSet("Check", "Record")]
  [string]$Action = "Check"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$VenvPython = Join-Path $Root ".venv\Scripts\python.exe"
$RuntimeRoot = if ($env:HERMES_WORKSTATION_HOME) {
  [System.IO.Path]::GetFullPath($env:HERMES_WORKSTATION_HOME)
} else {
  Join-Path $env:LOCALAPPDATA "HermesWorkstation"
}
$StampFile = Join-Path $RuntimeRoot "Runtime\oneclick-dependencies.sha256"

function Get-InstallFingerprint {
  $patterns = @(
    "package.json", "package-lock.json", ".npmrc", ".nvmrc",
    "pyproject.toml", "uv.lock",
    "apps/*/package.json", "ui-tui/package.json",
    "ui-tui/packages/*/package.json", "web/package.json",
    "tests-js/package.json"
  )
  $parts = New-Object System.Collections.Generic.List[string]
  foreach ($pattern in $patterns) {
    $matches = @(Get-ChildItem -Path (Join-Path $Root $pattern) -File -ErrorAction SilentlyContinue)
    if ($matches.Count -eq 0) {
      $parts.Add("MISSING:$pattern")
    }
    foreach ($file in ($matches | Sort-Object FullName)) {
      $relative = $file.FullName.Substring($Root.Length).TrimStart('\')
      $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
      $parts.Add("$relative=$digest")
    }
  }
  if (-not (Get-Command node -ErrorAction SilentlyContinue) -or
      -not (Get-Command npm -ErrorAction SilentlyContinue)) {
    return $null
  }
  $nodeVersion = (& node --version 2>$null | Select-Object -Last 1)
  if ($LASTEXITCODE -ne 0) { return $null }
  $npmVersion = (& cmd.exe /d /c "npm --version 2>NUL" | Select-Object -Last 1)
  if ($LASTEXITCODE -ne 0) { return $null }
  $parts.Add("node=$nodeVersion")
  $parts.Add("npm=$npmVersion")
  $text = $parts -join "`n"
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($text)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try { return [BitConverter]::ToString($sha.ComputeHash($bytes)).Replace('-', '') }
  finally { $sha.Dispose() }
}

try {
  $fingerprint = Get-InstallFingerprint
  if (-not $fingerprint) { Write-Host "[deps] Toolchain unavailable."; exit 1 }
  $requiredPaths = @(
    $VenvPython,
    (Join-Path $Root "node_modules\.bin\vite.cmd"),
    (Join-Path $Root "node_modules\.bin\tsc.cmd"),
    (Join-Path $Root "apps\desktop\node_modules\.bin\electron.cmd"),
    (Join-Path $Root "node_modules\.bin\concurrently.cmd")
  )
  foreach ($path in $requiredPaths) {
    if (-not (Test-Path -LiteralPath $path)) {
      Write-Host "[deps] Missing: $path"
      exit 1
    }
  }
  & $VenvPython -c "import hermes_cli" 2>$null
  if ($LASTEXITCODE -ne 0) { Write-Host "[deps] Python environment needs repair."; exit 1 }
  if ($Action -eq "Record") {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $StampFile) | Out-Null
    [System.IO.File]::WriteAllText($StampFile, $fingerprint)
    Write-Host "[deps] Successful dependency install fingerprint recorded."
    exit 0
  }
  if ((Test-Path -LiteralPath $StampFile) -and
      ([System.IO.File]::ReadAllText($StampFile).Trim() -eq $fingerprint)) {
    Write-Host "[deps] Verified cached dependencies; install not required."
    exit 0
  }
  Write-Host "[deps] Dependency inputs changed (or no successful-install record); full install required."
  exit 1
} catch {
  Write-Host "[deps] Could not validate cached install: $($_.Exception.Message)"
  exit 1
}
