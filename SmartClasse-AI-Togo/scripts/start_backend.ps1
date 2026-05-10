param(
    [int]$Port = 8010,
    [string]$BindHost = '127.0.0.1'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot 'venv\Scripts\python.exe'
$healthUrl = "http://$BindHost`:$Port/health"

if (-not (Test-Path $python)) {
    throw "Python introuvable dans le venv: $python"
}

$listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
if ($listener) {
    Write-Host "Le port $Port est déjà occupé. Le backend peut déjà tourner."
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 5
        Write-Host ("Backend déjà actif: {0}" -f ($health | ConvertTo-Json -Compress))
        exit 0
    } catch {
        Write-Host "Un processus écoute sur le port $Port, mais /health n'est pas joignable."
        Write-Host "Arrêtez le processus existant puis relancez ce script."
        exit 1
    }
}

Write-Host "Démarrage du backend SmartClasse sur $healthUrl"

$arguments = @(
    '-m', 'uvicorn', 'src.main:app',
    '--host', $BindHost,
    '--port', $Port
)

$process = Start-Process -FilePath $python -ArgumentList $arguments -WorkingDirectory $repoRoot -PassThru

for ($attempt = 1; $attempt -le 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 2
        Write-Host ("Backend prêt: {0}" -f ($health | ConvertTo-Json -Compress))
        exit 0
    } catch {
        if ($process.HasExited) {
            throw "Le processus uvicorn s'est arrêté prématurément avec le code $($process.ExitCode)."
        }
    }
}

Write-Host "Le backend a été lancé mais n'a pas répondu dans le délai attendu."
Write-Host "Vérifiez la fenêtre Uvicorn ou relancez manuellement:"
Write-Host "  $python -m uvicorn src.main:app --host $BindHost --port $Port"
exit 1