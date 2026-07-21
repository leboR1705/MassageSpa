<#
start-ngrok.ps1

Opens two PowerShell windows:
- one activates the project's virtualenv and runs Django dev server on 127.0.0.1:8000
- the other starts ngrok forwarding to port 8000 (uses .\tools\ngrok.exe if present, otherwise the `ngrok` command)

Run from the project root:
    .\start-ngrok.ps1

#>

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Paths
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
$NgrokLocal = Join-Path $ProjectRoot "tools\ngrok.exe"
# Common alternate locations for ngrok
$NgrokOneDrive = Join-Path $env:USERPROFILE "OneDrive\Desktop\ngrok.exe"
$NgrokDownloads = Join-Path $env:USERPROFILE "Downloads\ngrok.exe"

## If an ngrok process is already running, stop it to ensure a fresh tunnel
$existing = Get-Process ngrok -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host 'Stopping existing ngrok process (PID:' $existing.Id ')'
    Stop-Process -Id $existing.Id -Force
    Start-Sleep -Milliseconds 500
}

if (-not (Test-Path $VenvActivate)) {
    Write-Host 'Warning: virtualenv activate script not found at' $VenvActivate -ForegroundColor Yellow
    Write-Host 'If your venv is elsewhere, edit this script or run the server manually.' -ForegroundColor Yellow
}

# Command to run Django (venv activation then runserver)
$DjangoCmd = "& '$VenvActivate'; Set-Location -Path '$ProjectRoot'; python manage.py runserver 127.0.0.1:8000"

# Command to run ngrok (prefer local tools\ngrok.exe). Use unquoted host-header value to avoid parsing issues.
## Choose the ngrok executable to run (prefer project tools, then OneDrive desktop, then Downloads, then system `ngrok`)
if (Test-Path $NgrokLocal) {
    $NgrokExe = $NgrokLocal
} elseif (Test-Path $NgrokOneDrive) {
    $NgrokExe = $NgrokOneDrive
} elseif (Test-Path $NgrokDownloads) {
    $NgrokExe = $NgrokDownloads
} else {
    $NgrokExe = $null
}

if ($NgrokExe) {
    $NgrokCmd = "& '$NgrokExe' http 8000 --host-header=localhost:8000"
} else {
    # fallback to system ngrok command (requires ngrok on PATH)
    $NgrokCmd = "ngrok http 8000 --host-header=localhost:8000"
}

Write-Host 'Starting Django in a new PowerShell window...'
Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command',$DjangoCmd

Start-Sleep -Seconds 1

Write-Host 'Starting ngrok in a new PowerShell window...'
Start-Process -FilePath powershell -ArgumentList '-NoExit','-Command',$NgrokCmd

# Wait for ngrok web API (127.0.0.1:4040) to become available and print the public URL(s)
$maxAttempts = 60
$attempt = 0

$tunnels = $null
Write-Host 'Waiting for ngrok web UI at http://127.0.0.1:4040 (also trying localhost)...' -ForegroundColor Cyan
while ($attempt -lt $maxAttempts -and -not $tunnels) {
    try {
        # try both IPv4 loopback and hostname
        try { $tunnels = Invoke-RestMethod http://127.0.0.1:4040/api/tunnels -ErrorAction Stop }
        catch { $tunnels = Invoke-RestMethod http://localhost:4040/api/tunnels -ErrorAction Stop }
    } catch {
        Start-Sleep -Seconds 1
        $attempt++
    }
}

if ($tunnels -and $tunnels.tunnels) {
    $public = $tunnels.tunnels | ForEach-Object { $_.public_url }
    Write-Host 'ngrok public URL(s):' -ForegroundColor Green
    $public | ForEach-Object { Write-Host " - $_" }
    Write-Host 'Open http://127.0.0.1:4040 to inspect ngrok traffic.' -ForegroundColor Green
    
    # Copy first public URL to clipboard for easy pasting
    $firstUrl = $public | Select-Object -First 1
    if ($firstUrl) {
        try {
            Set-Clipboard -Value $firstUrl
            Write-Host "Public URL copied to clipboard: $firstUrl" -ForegroundColor Green
        } catch {
            Write-Host "Could not copy to clipboard: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    # Perform a quick test request to each public URL using a browser-like User-Agent
    foreach ($url in $public) {
        Write-Host "Testing $url ..." -ForegroundColor Cyan
        try {
            $resp = Invoke-WebRequest $url -Headers @{ 'User-Agent' = 'Mozilla/5.0' } -UseBasicParsing -TimeoutSec 15
            Write-Host " -> Status: $($resp.StatusCode)" -ForegroundColor Green
            if ($resp.Content) {
                $preview = $resp.Content
                if ($preview.Length -gt 400) { $preview = $preview.Substring(0,400) + '... (truncated)' }
                Write-Host " -> Response preview:\n$preview" -ForegroundColor DarkGray
            }
        } catch {
            Write-Host " -> Request failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    # Also test with ngrok-skip-browser-warning header to bypass interstitial
    foreach ($url in $public) {
        Write-Host "Testing $url with ngrok-skip-browser-warning header..." -ForegroundColor Cyan
        try {
            $resp2 = Invoke-WebRequest $url -Headers @{ 'User-Agent'='Mozilla/5.0'; 'ngrok-skip-browser-warning'='1' } -UseBasicParsing -TimeoutSec 15
            Write-Host " -> Skip-header Status: $($resp2.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host " -> Skip-header request failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host 'ngrok web API did not become available within the timeout. Check the ngrok window for errors.' -ForegroundColor Yellow
}
