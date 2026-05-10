param(
    [int]$InitialSizeMB = 16384,
    [int]$MaximumSizeMB = 32768,
    [string]$PageFilePath = "C:\\pagefile.sys"
)

$ErrorActionPreference = "Stop"

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Ensure-Admin {
    if (Test-IsAdmin) {
        return
    }

    Write-Host "Redemarrage en mode administrateur..." -ForegroundColor Yellow
    $args = @(
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$PSCommandPath`"",
        "-InitialSizeMB", $InitialSizeMB,
        "-MaximumSizeMB", $MaximumSizeMB,
        "-PageFilePath", "`"$PageFilePath`""
    )

    Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs | Out-Null
    exit 0
}

function Set-PageFileConfiguration {
    Write-Host "Configuration pagefile pour Gemma 4 e4b..." -ForegroundColor Cyan
    Write-Host "Initial: $InitialSizeMB MB | Max: $MaximumSizeMB MB | Fichier: $PageFilePath"

    $cs = Get-CimInstance -ClassName Win32_ComputerSystem
    if ($cs.AutomaticManagedPagefile) {
        Write-Host "Desactivation de la gestion automatique du pagefile..."
        Set-CimInstance -InputObject $cs -Property @{ AutomaticManagedPagefile = $false } | Out-Null
    }

    $escapedPath = $PageFilePath.Replace("\\", "\\\\")
    $existing = Get-CimInstance -ClassName Win32_PageFileSetting -Filter "Name = '$escapedPath'" -ErrorAction SilentlyContinue

    if (-not $existing) {
        Write-Host "Creation de l'entree pagefile..."
        $new = New-CimInstance -ClassName Win32_PageFileSetting -Property @{
            Name = $PageFilePath
            InitialSize = $InitialSizeMB
            MaximumSize = $MaximumSizeMB
        }
        $existing = $new
    }

    Write-Host "Mise a jour des tailles du pagefile..."
    Set-CimInstance -InputObject $existing -Property @{
        InitialSize = $InitialSizeMB
        MaximumSize = $MaximumSizeMB
    } | Out-Null

    Write-Host "\nConfiguration appliquee. Verification:" -ForegroundColor Green
    Get-CimInstance Win32_ComputerSystem | Select-Object AutomaticManagedPagefile | Format-Table -AutoSize
    Get-CimInstance Win32_PageFileSetting | Select-Object Name, InitialSize, MaximumSize | Format-Table -AutoSize

    Write-Host "\nImportant: Redemarrez Windows pour activer la nouvelle taille de pagefile." -ForegroundColor Yellow
}

Ensure-Admin
Set-PageFileConfiguration