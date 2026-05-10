param(
    [int]$Port = 8010,
    [string]$BindHost = '127.0.0.1'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$healthUrl = "http://$BindHost`:$Port/health"
$composeFile = Join-Path $repoRoot 'docker-compose.yml'

if (-not (Test-Path $composeFile)) {
    throw "docker-compose.yml introuvable: $composeFile"
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

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker n'est pas disponible dans le PATH. Installez Docker Desktop avant de lancer le backend."
}

try {
    docker info | Out-Null
} catch {
    throw "Le démon Docker n'est pas disponible. Démarrez Docker Desktop puis relancez ce script."
}

Write-Host "Démarrage du backend SmartClasse via Docker sur $healthUrl"

$arguments = @(
    'compose',
    '-f', $composeFile,
    'up',
    '--build',
    '-d',
    'backend'
)

& docker @arguments

for ($attempt = 1; $attempt -le 60; $attempt++) {
    Start-Sleep -Milliseconds 1000
    try {
        $health = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 2
        Write-Host ("Backend prêt: {0}" -f ($health | ConvertTo-Json -Compress))
        exit 0
    } catch {
        continue
    }
}

Write-Host "Le backend a été lancé mais n'a pas répondu dans le délai attendu."
Write-Host "Vérifiez les logs Docker avec:"
Write-Host "  docker compose -f `"$composeFile`" logs -f backend"
exit 1