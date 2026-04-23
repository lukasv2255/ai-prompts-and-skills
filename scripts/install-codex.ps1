$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceSkills = Join-Path $repoRoot "shared-skills"
$sourceAgents = Join-Path $repoRoot "codex\\AGENTS.md"
$sourceConfig = Join-Path $repoRoot "codex\\config.template.toml"
$codexRoot = Join-Path $HOME ".codex"
$agentsRoot = Join-Path $HOME ".agents"
$targetSkills = Join-Path $agentsRoot "skills"
$targetAgents = Join-Path $codexRoot "AGENTS.md"
$targetConfig = Join-Path $codexRoot "config.toml"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

New-Item -ItemType Directory -Force -Path $codexRoot | Out-Null
New-Item -ItemType Directory -Force -Path $agentsRoot | Out-Null
New-Item -ItemType Directory -Force -Path $targetSkills | Out-Null

Copy-Item -Force $sourceAgents $targetAgents

if (-not (Test-Path $targetConfig)) {
    Copy-Item -Force $sourceConfig $targetConfig
}

Get-ChildItem -Path $sourceSkills -Directory | ForEach-Object {
    $name = $_.Name
    $target = Join-Path $targetSkills $name

    if (Test-Path $target) {
        $existing = Get-Item $target -Force
        if ($existing.Attributes.ToString().Contains("ReparsePoint")) {
            Remove-Item -LiteralPath $target -Force
        } else {
            Move-Item -LiteralPath $target -Destination "$target.backup-$timestamp"
        }
    }

    New-Item -ItemType Junction -Path $target -Target $_.FullName | Out-Null
}

Write-Host "Codex setup complete."
Write-Host "AGENTS.md copied to $targetAgents"
Write-Host "Skills linked into $targetSkills"
