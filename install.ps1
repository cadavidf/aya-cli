# Installs Aya on Windows (PowerShell 5.1 or newer). Run from a checkout, or piped: irm <url> | iex
# It never installs Ollama or models.
$ErrorActionPreference = 'Stop'
$zip = if ($env:AYA_ZIP) { $env:AYA_ZIP } else { 'https://github.com/cadavidf/aya/archive/refs/heads/main.zip' }
$root = Join-Path $env:LOCALAPPDATA 'Aya'
$bin = Join-Path $root 'bin'

function Fail($msg) { Write-Host "Error: $msg" -ForegroundColor Red; throw $msg }

# Find a working Python 3.8+ (the "python" command may be a Microsoft Store stub).
$py = $null
foreach ($c in @(@('py', '-3'), @('python'), @('python3'))) {
    if (-not (Get-Command $c[0] -ErrorAction SilentlyContinue)) { continue }
    $args2 = @($c | Select-Object -Skip 1) + @('-c', 'import sys; sys.exit(sys.version_info < (3, 8))')
    try { & $c[0] @args2 2>$null } catch { continue }
    if ($LASTEXITCODE -eq 0) { $py = $c; break }
}
if (-not $py) { Fail 'Python 3.8 or newer is required. Install it from https://www.python.org/downloads/ (or: winget install Python.Python.3.12), then rerun.' }

$src = if ($PSCommandPath -and (Test-Path (Join-Path (Split-Path $PSCommandPath) 'aya.py'))) { Split-Path $PSCommandPath } else { $null }
if (-not $src) {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("aya-" + [guid]::NewGuid())
    New-Item -ItemType Directory $tmp | Out-Null
    try {
        Write-Host 'Downloading Aya...'
        try { Invoke-WebRequest $zip -OutFile (Join-Path $tmp 'aya.zip') -UseBasicParsing } catch { Fail "download failed: $zip" }
        Expand-Archive (Join-Path $tmp 'aya.zip') -DestinationPath (Join-Path $tmp 'x')
        $inner = Get-ChildItem (Join-Path $tmp 'x') -Directory | Select-Object -First 1
        if (-not (Test-Path (Join-Path $inner.FullName 'aya.py'))) { Fail 'the download does not contain aya.py.' }
        $code = Join-Path $root 'app'
        if (Test-Path $code) { Remove-Item $code -Recurse -Force }
        New-Item -ItemType Directory $root -Force | Out-Null
        Move-Item $inner.FullName $code
        $src = $code
    } finally { Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

New-Item -ItemType Directory $bin -Force | Out-Null
$launcher = Join-Path $bin 'aya.cmd'
$pyCmd = $py -join ' '
Set-Content $launcher -Encoding ASCII "@echo off`r`n$pyCmd `"$src\aya.py`" %*"
Write-Host "Installed $launcher (code in $src)"

$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($userPath -split ';') -notcontains $bin) {
    $ans = Read-Host "Add $bin to your user PATH? [y/N]"
    if ($ans -match '^[yY]') {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$bin", 'User')
        Write-Host 'Done. Open a new terminal to use: aya'
    } else {
        Write-Host "Not changed. Run Aya with: & '$launcher'"
    }
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host 'Ollama is not installed. Aya needs it: https://ollama.com/download/windows'
    Write-Host 'Then run: ollama pull dolphin3:latest'
} elseif (-not (& { $ErrorActionPreference = 'SilentlyContinue'; ollama list 2>$null | Select-String '^dolphin3:latest' })) {
    Write-Host 'Ollama is installed, but dolphin3:latest was not found (or Ollama is not running).'
    Write-Host 'Start the Ollama app, then run: ollama pull dolphin3:latest'
}
Write-Host 'Start Aya with: aya'
