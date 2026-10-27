<#
.SYNOPSIS
  Windows PowerShell version of the course's Kestra setup (03-orchestration/03-setup.md).

.DESCRIPTION
  1. Reads API keys from the project root .env (never from this script).
  2. Base64-encodes them into SECRET_* environment variables, as Kestra expects.
  3. Runs `docker compose up -d` in this folder.
  4. Waits for http://localhost:8080 and imports every flow in .\flows.

  Course bash equivalent:
    export SECRET_GEMINI_API_KEY=$(echo -n $GEMINI_API_KEY | base64)
    docker compose up -d
    curl -X POST -u 'admin@kestra.io:Admin1234!' http://localhost:8080/api/v1/flows/import -F fileUpload=@flows/...

.EXAMPLE
  .\start-kestra.ps1            # start Kestra and import flows
  .\start-kestra.ps1 -DryRun    # only check which keys are present
#>
param([switch]$DryRun)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path (Split-Path -Parent $here) ".env"

# ---- 1. read .env ----
$vals = @{}
if (Test-Path $envFile) {
    foreach ($line in Get-Content $envFile) {
        if ($line -match '^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$') { $vals[$Matches[1]] = $Matches[2].Trim('"', "'") }
    }
} else {
    Write-Warning ".env not found at $envFile"
}

function Is-Real($v) { return $v -and ($v -notmatch 'YOUR_KEY|your_key|\.\.\.$|_here$') }

$keys = [ordered]@{
    GEMINI_API_KEY = "required (flows 1, 2, 4, 5, 6 + AI Copilot)"
    TAVILY_API_KEY = "flows 3, 5, 6 (web search)"
    GROQ_API_KEY   = "flow 3_rag_with_websearch_groq"
    OPENAI_API_KEY = "course flow 3 only (optional, Groq version replaces it)"
}

# ---- 2. SECRET_* = base64(value) ----
foreach ($k in $keys.Keys) {
    $v = $vals[$k]
    if (Is-Real $v) {
        $b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($v))
        Set-Item -Path "Env:SECRET_$k" -Value $b64
        Write-Host ("  OK       {0,-15} ({1})" -f $k, $keys[$k])
    } else {
        Set-Item -Path "Env:SECRET_$k" -Value ""
        Write-Host ("  MISSING  {0,-15} ({1})" -f $k, $keys[$k]) -ForegroundColor Yellow
    }
}
# AI Copilot reads the raw (not base64) Gemini key
$env:GEMINI_API_KEY = if (Is-Real $vals["GEMINI_API_KEY"]) { $vals["GEMINI_API_KEY"] } else { "" }

if ($DryRun) { Write-Host "Dry run: not starting Docker."; return }

# ---- 3. docker compose up ----
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed. Install Docker Desktop (https://www.docker.com/products/docker-desktop/), start it, then re-run."
}
Push-Location $here
try { docker compose up -d } finally { Pop-Location }

# ---- 4. wait for Kestra, import flows ----
$cred = "admin@kestra.io:Admin1234!"
Write-Host "Waiting for Kestra on http://localhost:8080 ..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    $code = & curl.exe -s -o NUL -w "%{http_code}" -u $cred http://localhost:8080/api/v1/flows/search
    if ($code -eq "200") { $ready = $true; break }
    Start-Sleep -Seconds 5
}
if (-not $ready) { throw "Kestra did not come up within 5 minutes. Check: docker compose logs kestra" }

foreach ($f in Get-ChildItem (Join-Path $here "flows") -Filter *.yaml) {
    $code = & curl.exe -s -o NUL -w "%{http_code}" -X POST -u $cred `
        http://localhost:8080/api/v1/flows/import -F "fileUpload=@$($f.FullName)"
    Write-Host ("  import {0,-35} HTTP {1}" -f $f.Name, $code)
}
Write-Host "Kestra UI: http://localhost:8080  (login admin@kestra.io / Admin1234!)  namespace: zoomcamp"
