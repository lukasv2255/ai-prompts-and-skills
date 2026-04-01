$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceSkills = Join-Path $repoRoot "shared-skills"
$sourceConfig = Join-Path $repoRoot "codex\\config.template.toml"
$codexRoot = Join-Path $HOME ".codex"
$skillsRoot = Join-Path $codexRoot "skills"
$targetSkills = Join-Path $skillsRoot "tommy"
$targetConfig = Join-Path $codexRoot "config.toml"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

New-Item -ItemType Directory -Force -Path $codexRoot | Out-Null
New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null

if (Test-Path $targetSkills) {
    $existing = Get-Item $targetSkills -Force
    if (-not $existing.Attributes.ToString().Contains("ReparsePoint")) {
        Move-Item -LiteralPath $targetSkills -Destination "$targetSkills.backup-$timestamp"
    } else {
        Remove-Item -LiteralPath $targetSkills -Force
    }
}

New-Item -ItemType Junction -Path $targetSkills -Target $sourceSkills | Out-Null

if (-not (Test-Path $targetConfig)) {
    Copy-Item -Force $sourceConfig $targetConfig
}

Write-Host "Codex setup complete."
Write-Host "Skills linked from $sourceSkills"
