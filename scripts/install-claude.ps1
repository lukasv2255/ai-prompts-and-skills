$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$sourceSkills = Join-Path $repoRoot "shared-skills"
$sourceClaude = Join-Path $repoRoot "claude"
$claudeRoot = Join-Path $HOME ".claude"
$targetSkills = Join-Path $claudeRoot "skills"
$targetClaudeMd = Join-Path $claudeRoot "CLAUDE.md"
$targetAgents = Join-Path $claudeRoot "agents"
$targetHooks = Join-Path $claudeRoot "hooks"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

New-Item -ItemType Directory -Force -Path $claudeRoot | Out-Null
New-Item -ItemType Directory -Force -Path $targetAgents | Out-Null
New-Item -ItemType Directory -Force -Path $targetHooks | Out-Null

if (Test-Path $targetSkills) {
    $existing = Get-Item $targetSkills -Force
    if (-not $existing.Attributes.ToString().Contains("ReparsePoint")) {
        Move-Item -LiteralPath $targetSkills -Destination "$targetSkills.backup-$timestamp"
    } else {
        Remove-Item -LiteralPath $targetSkills -Force
    }
}

New-Item -ItemType Junction -Path $targetSkills -Target $sourceSkills | Out-Null
Copy-Item -Force (Join-Path $sourceClaude "CLAUDE.md") $targetClaudeMd
Copy-Item -Force (Join-Path $sourceClaude "agents\\code-reviewer.md") (Join-Path $targetAgents "code-reviewer.md")
Copy-Item -Force (Join-Path $sourceClaude "hooks\\check-project-structure.sh") (Join-Path $targetHooks "check-project-structure.sh")

Write-Host "Claude setup complete."
Write-Host "Skills linked from $sourceSkills"
