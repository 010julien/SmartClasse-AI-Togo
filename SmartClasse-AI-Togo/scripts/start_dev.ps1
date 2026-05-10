param(
    [int]$Port = 8010,
    [string]$BindHost = '127.0.0.1'
)

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendScript = Join-Path $PSScriptRoot 'start_backend.ps1'
$flutterClientDir = Join-Path $repoRoot 'flutter_client'

if (-not (Test-Path $backendScript)) {
    throw "Script backend introuvable: $backendScript"
}

Write-Host "== SmartClasse dev launcher =="
Write-Host "1) Démarrage du backend"

& $backendScript -Port $Port -BindHost $BindHost

Write-Host ""
Write-Host "2) Backend prêt. Lance maintenant le client Flutter dans une autre fenêtre terminal:"
Write-Host "   cd `"$flutterClientDir`""
Write-Host "   flutter run -d chrome"
Write-Host ""
Write-Host "Si tu veux une exécution complète en une seule fenêtre, ouvre un second terminal pour Flutter après ce script."