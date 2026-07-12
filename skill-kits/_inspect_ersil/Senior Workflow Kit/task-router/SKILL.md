---
name: task-router
description: Choose the cheapest reliable model, effort level, and workflow for a task. Use before expensive reasoning, large code work, multi-agent tasks, research, audits, or any job where cost/quality trade-offs matter.
---

# Task Router

Route this task: `$ARGUMENTS`

The goal is not to always use the strongest model. The goal is to spend intelligence where it changes the outcome, and use cheaper workers for bounded evidence gathering, extraction, boilerplate, and repetitive checks.

## Routing inputs

Evaluate the task on these dimensions:

- **Ambiguity**: Are goals, constraints, and success criteria clear?
- **Risk**: Can mistakes cause production, security, financial, legal, brand, or user-trust damage?
- **Reversibility**: Can the output be cheaply corrected?
- **Context size**: Does the task require reading many files, long docs, logs, or history?
- **Taste/judgment**: Does quality depend on UX, strategy, positioning, narrative, or creative judgment?
- **Freshness**: Does current information materially affect the answer?
- **Execution load**: Is the work repetitive once the plan is known?

## Task bands

| Band | Use case | Recommended route |
|---|---|---|
| A | Tiny edits, formatting, simple rewrites, obvious answers | Fast capable model, low effort |
| B | Extraction, summarization, search, first-pass mapping | Fast/cheap scout, low–medium effort |
| C | Bounded implementation or content with clear specs | Standard strong worker, medium effort |
| D | Debugging, architecture, unclear requirements, cross-file reasoning | Senior model or standard worker with Precision Mode, high effort |
| E | Production risk, security, major architecture, legal/financial sensitivity, high-value creative strategy | Senior orchestrator + independent verifier, high or extra-high effort |
| F | Deep research, broad design space, irreversible decisions, high cost of error | Senior orchestration, multiple scouts, independent audit; avoid maximum effort unless truly justified |

## Model role mapping

In this Personal OS the roles map to concrete Agent tool models (see CLAUDE.md, section Model Routing): Fast scout = `haiku`, Standard builder = `sonnet`, Senior operator = `opus`. Reserve `fable` for band E/F work where nothing cheaper holds. Always pass the `model` parameter explicitly when spawning subagents.

### Fast scout

Use for:

- Searching files and docs.
- Extracting structured facts.
- Summarizing low-risk material.
- Listing options, examples, or obvious gaps.
- Creating boilerplate from precise instructions.

Do not use alone for final decisions when the task is ambiguous, high-risk, security-sensitive, or taste-heavy.

### Standard builder

Use for:

- Main implementation with a scoped plan.
- Moderate debugging.
- Refactoring within clear boundaries.
- Test creation.
- Polished drafts from a clear brief.
- Reviewing scout output.

### Senior operator

Use for:

- Framing unclear work.
- Architecture, trade-offs, and strategy.
- Adversarial review.
- Creative taste or UX judgment.
- Final verification of high-impact work.
- Designing workflows for cheaper workers.

Do not use a senior model as a repetitive workhorse after the plan is clear.

## Effort selection

- **low**: short, deterministic, low-risk, reversible.
- **medium**: normal work with adequate context and limited risk.
- **high**: ambiguity, cross-file reasoning, debugging, planning, or meaningful judgment.
- **extra-high**: high impact, many dependencies, security/privacy risk, or difficult verification.
- **maximum**: only when the cost of a miss is very high and extra analysis is more valuable than speed/cost.

Higher effort can overcomplicate simple problems. If output becomes speculative, narrow the task and lower the effort.

## Recommended workflow

When tools/subagents are available:

1. Senior operator defines outcome, acceptance criteria, risks, and the work split.
2. Fast scout gathers evidence only; no final decisions.
3. Standard builder executes a narrow, testable plan.
4. Independent auditor verifies against requirements and evidence.
5. Senior operator writes the final calibrated response.

When subagents are unavailable, simulate the roles sequentially in one run.

## Output format

Return:

- **Task band**
- **Recommended model/effort**
- **Workflow**
- **Delegated work**
- **Work that must stay with a senior model**
- **Verification plan**
- **Cost-control notes**
