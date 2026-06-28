---
name: security-review
description: Use this skill to perform a security review of a Node.js or Python
  codebase and report findings ranked by severity — injection (SQL/command/
  template), XSS, auth and authorization flaws (including IDOR), secret handling,
  unsafe deserialization, path traversal, dangerous side-effects (sending mail,
  money, deleting data), prompt-injection-driven actions, and risky dependencies.
  Trigger this whenever the user asks to "review", "audit", "check the security
  of", "find vulnerabilities in", or "harden" their code or project, even if they
  don't say the word "security" explicitly. This skill REPORTS findings only — it
  does not modify code. It works best after the project-analyzer skill has produced
  a PROJECT MAP; if none exists, offer to run that first.
---

# Security Review (Node.js / Python)

## Overview

Reviews code for security issues and reports honest, actionable findings ranked
by severity. This is **judgment work**, not pattern-matching: read the code,
reason about what an attacker actually controls, and trace untrusted input to
where it causes harm. Report uncertainty plainly and say "no issue found" when
that is the truth — do not invent vulnerabilities to look thorough.

**This skill reports only. It does not edit code or apply fixes.** It may include
a suggested fix in text/code-sketch form for each finding, but never modifies the
project.

## Prerequisites

- A **PROJECT MAP** from the `project-analyzer` skill gives you the attack surface
  for free. If one exists in the conversation, use it. If not, offer to run
  project-analyzer first — reviewing blind wastes effort. If the user declines,
  do a quick orientation pass yourself before reviewing.

## Workflow

1. **Prioritize by attack surface.** Using the PROJECT MAP, order the review:
   external input surfaces → auth/authz → secrets → side-effects → everything else.
   The biggest risks live where untrusted input meets a powerful action.
2. **Review in chunks.** Never dump the whole repo into one pass — attention drops
   on huge inputs and findings get missed. One concern area (or one module) per pass.
3. **Consult the per-language checklist** in `references/checklist.md` for the
   relevant stack (Node and/or Python) as you go.
4. **Classify each finding** using `references/severity.md`.
5. **Second pass on the dangerous stuff.** After the main review, do a dedicated
   pass over (a) all authorization checks and (b) any code with side-effects —
   sending mail, moving money, deleting/writing data, shelling out. Ask for each:
   *can untrusted input reach this, including via prompt injection?*

## What to check (high level — details in references/checklist.md)

- **Inputs:** SQL/NoSQL/command/template injection, XSS, unsafe deserialization,
  path traversal, SSRF, unvalidated LLM/tool output that drives an action.
- **Auth & authz:** missing or wrong checks, IDOR (user A can read/modify user B's
  data), broken session/token handling, privilege escalation, missing rate limits
  on auth endpoints.
- **Secrets:** hardcoded keys/passwords, secrets in logs or error messages, weak
  or home-rolled crypto, weak password hashing (plain/MD5/SHA1 vs bcrypt/argon2).
- **Side-effects:** anything that sends mail, money, or deletes/writes data — can
  it be triggered by untrusted input? For agents: can prompt injection in incoming
  content cause an unintended send/action?
- **Dependencies:** versions flagged in the PROJECT MAP that are outdated or known-
  risky. Note them; don't fabricate CVE numbers you can't verify.

## Known limits — state these to the user in the report

- Reviews what **is** in the code, not what's **missing** by design.
- Weak on business-logic flaws, race conditions, and deployment/infra misconfig
  (publicly exposed DB, missing rate limiting at the edge, bad TLS).
- For payments, health/PII, or any high-value target, recommend a human pentest /
  professional audit on top of this review.

## Output format

Start with a one-line scope statement (what was and wasn't reviewed). Then, for
each finding:

- **[SEVERITY] Title** — Critical / High / Medium / Low / Info
- **Location:** `file:line`
- **Why it's exploitable:** the attacker's concrete path, not a generic warning.
- **Suggested fix:** specific, with a short code sketch if helpful. (Suggestion
  only — this skill does not apply changes.)

End with a **Summary**: counts by severity, the top 3 to fix first, and the
"Known limits" caveat above. If you found nothing in an area, say so explicitly.

## Tone

Be honest and proportionate. Don't inflate severity to seem useful, and don't
soften a real Critical. If you're unsure whether something is exploitable, say so
and explain what would confirm it.
