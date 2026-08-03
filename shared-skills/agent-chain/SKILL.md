---
name: agent-chain
description: Design a cost-aware multi-agent workflow for complex work. Splits tasks into scouting, building, review, and final synthesis while keeping expensive reasoning focused on judgment.
---

# Agent Chain

Design an agent workflow for: `$ARGUMENTS`

Create a practical multi-agent plan that uses senior reasoning for judgment and cheaper workers for bounded, repeatable execution.

## Workflow design rules

- Start from the outcome, not from the agents.
- Define success criteria before delegation.
- Keep each worker prompt narrow and verifiable.
- Use read-only scouts for evidence gathering.
- Use builders only after scope and constraints are clear.
- Use an independent auditor before the final answer.
- Avoid circular delegation and vague "review everything" prompts.
- Escalate to a senior model only for ambiguity, risk, architecture, taste, or final judgment.

## Default roles

All five roles exist as local subagent definitions in `.claude/agents/` (`lead-operator`, `evidence-scout`, `implementation-worker`, `quality-auditor`, `taste-editor`) with model tiers already set. Prefer spawning them over ad-hoc prompts; model mapping lives in CLAUDE.md, section Model Routing.

### Lead operator

Owns:

- Final goal.
- Acceptance criteria.
- Task split.
- Risk register.
- Final synthesis.

### Evidence scout

Owns:

- File/doc/source discovery.
- Fact extraction.
- Current-state map.
- Missing-context report.

Scout must not make final decisions.

### Builder

Owns:

- Implementation or deliverable creation from a precise brief.
- Minimal changes.
- Local conventions.
- Initial checks.

### Quality auditor

Owns:

- Independent verification.
- Requirement coverage.
- Tests/checks review.
- Edge cases and risk findings.

### Taste editor

Use only when the deliverable depends on UI, UX, copy, brand, narrative, creative direction, or presentation quality.

## Plan structure

Return a workflow with:

1. **Goal**
2. **Acceptance criteria**
3. **Risk profile**
4. **Agent roles and model tier**
5. **Exact worker prompts**
6. **Handoff format between agents**
7. **Verification plan**
8. **Stop conditions**
9. **Final response format**

## Worker prompt requirements

Each worker prompt must include:

- Specific objective.
- Allowed tools or files.
- What not to do.
- Expected output format.
- Evidence requirement.
- Maximum scope.

## Cost controls

- Batch cheap scouting before senior review.
- Do not ask expensive models to summarize raw material unless judgment is needed.
- Use senior review after evidence is compressed.
- Stop early when evidence disproves the plan.
- Prefer one strong verification pass over repeated unstructured retries.
