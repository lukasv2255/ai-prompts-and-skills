#!/usr/bin/env python3
"""
scan_project.py — Factual inventory of a Node.js / Python project.

Emits JSON describing the stack, dependencies, entry points, external input
surfaces, and sensitive files. It does NOT judge security — it only locates
things worth a human/LLM look. Pattern-matching is intentionally broad; the
caller is expected to verify findings by reading the flagged files.

Usage:
    python3 scan_project.py <project_root> [--max-files N]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Directories we never descend into.
SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__",
    "dist", "build", ".next", ".nuxt", "coverage", ".pytest_cache",
    ".mypy_cache", ".cache", "site-packages", ".tox", "vendor",
}

# Files that signal a stack / hold dependencies.
MANIFESTS = {
    "package.json": "node",
    "package-lock.json": "node",
    "yarn.lock": "node",
    "pnpm-lock.yaml": "node",
    "tsconfig.json": "node",
    "requirements.txt": "python",
    "pyproject.toml": "python",
    "Pipfile": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "poetry.lock": "python",
}

# Filename hints for entry points.
ENTRY_HINTS = re.compile(
    r"(^|/)(index|main|app|server|cli|__main__|wsgi|asgi|manage|worker|"
    r"cron|scheduler|agent|bot|run)\.(js|ts|mjs|cjs|py)$",
    re.IGNORECASE,
)

# Source-content patterns grouped by concern. Each is (label, regex).
CONTENT_PATTERNS = {
    "entry_point": [
        ("express/fastify app", re.compile(r"\b(express|fastify)\s*\(")),
        ("http server", re.compile(r"\b(createServer|http\.Server|app\.listen)\b")),
        ("flask/fastapi app", re.compile(r"\b(Flask|FastAPI)\s*\(")),
        ("argparse/click cli", re.compile(r"\b(argparse|click|ArgumentParser)\b")),
        ("__main__ guard", re.compile(r"__name__\s*==\s*['\"]__main__['\"]")),
    ],
    "external_input": [
        ("http route", re.compile(r"\.(get|post|put|patch|delete)\s*\(\s*['\"]")),
        ("fastapi route", re.compile(r"@\w+\.(get|post|put|patch|delete)\s*\(")),
        ("flask route", re.compile(r"@\w+\.route\s*\(")),
        ("request body/params", re.compile(r"\b(req\.(body|query|params)|request\.(json|form|args))\b")),
        ("env var read", re.compile(r"\b(process\.env|os\.environ|os\.getenv)\b")),
        ("file read", re.compile(r"\b(readFile|open\s*\(|read_text|fs\.read)\b")),
        ("webhook/incoming", re.compile(r"\bwebhook\b", re.IGNORECASE)),
        ("llm/model output", re.compile(r"\b(messages\.create|chat\.completions|llm|completion|model\.generate)\b", re.IGNORECASE)),
    ],
    "auth": [
        ("auth/token/session", re.compile(r"\b(jwt|jsonwebtoken|passport|oauth|bcrypt|session|authenticate|authorization)\b", re.IGNORECASE)),
        ("password handling", re.compile(r"\b(password|passwd|hashpw|pbkdf2|scrypt|argon2)\b", re.IGNORECASE)),
    ],
    "secrets": [
        ("possible hardcoded secret", re.compile(r"(api[_-]?key|secret|token|password|passwd|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.IGNORECASE)),
        ("aws-style key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ],
    "database": [
        ("sql query", re.compile(r"\b(SELECT|INSERT|UPDATE|DELETE)\s+.*\b(FROM|INTO|SET)\b", re.IGNORECASE)),
        ("orm/db client", re.compile(r"\b(prisma|sequelize|mongoose|sqlalchemy|psycopg2|pymongo|knex|typeorm)\b", re.IGNORECASE)),
        ("string-built query", re.compile(r"(query|execute)\s*\(\s*[`'\"].*\$\{|%s.*%|\+\s*req\.", re.IGNORECASE)),
    ],
    "side_effects": [
        ("send mail", re.compile(r"\b(nodemailer|sendmail|smtplib|sendgrid|ses\.|mailgun|send_message|sendMail)\b", re.IGNORECASE)),
        ("shell execution", re.compile(r"\b(child_process|exec\s*\(|execSync|spawn|os\.system|subprocess|eval\s*\(|Function\s*\()\b")),
        ("outbound http", re.compile(r"\b(fetch\s*\(|axios|requests\.(get|post)|httpx|urllib)\b")),
        ("file write/delete", re.compile(r"\b(writeFile|unlink|rmdir|os\.remove|shutil\.rmtree|fs\.rm)\b")),
        ("payments", re.compile(r"\b(stripe|paypal|braintree|charge|payment)\b", re.IGNORECASE)),
    ],
}

SOURCE_EXT = {".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx", ".py"}
MAX_BYTES = 400_000  # skip files larger than this when scanning content


def iter_files(root: Path, max_files: int):
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            yield p
            count += 1
            if count >= max_files:
                return


def rel(root: Path, p: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def read_deps(root: Path, manifest_paths):
    deps = {}
    for mp in manifest_paths:
        name = mp.name
        try:
            text = mp.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if name == "package.json":
            try:
                data = json.loads(text)
                for key in ("dependencies", "devDependencies"):
                    for dep, ver in (data.get(key) or {}).items():
                        deps[dep] = str(ver)
            except json.JSONDecodeError:
                pass
        elif name == "requirements.txt":
            for line in text.splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    m = re.split(r"[=<>!~ ]", line, 1)
                    deps[m[0]] = line[len(m[0]):].strip() or "*"
    return deps


def scan():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--max-files", type=int, default=5000)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(json.dumps({"error": f"path not found: {root}"}))
        sys.exit(1)

    languages = set()
    manifest_paths = []
    entry_points = set()
    findings = {k: [] for k in CONTENT_PATTERNS}
    file_count = 0

    for p in iter_files(root, args.max_files):
        file_count += 1
        name = p.name

        if name in MANIFESTS:
            languages.add(MANIFESTS[name])
            manifest_paths.append(p)

        rpath = rel(root, p)
        if ENTRY_HINTS.search(rpath.replace(os.sep, "/")):
            entry_points.add(rpath)

        if p.suffix.lower() not in SOURCE_EXT:
            continue
        try:
            if p.stat().st_size > MAX_BYTES:
                continue
            content = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for concern, patterns in CONTENT_PATTERNS.items():
            for label, rx in patterns:
                m = rx.search(content)
                if m:
                    line_no = content[: m.start()].count("\n") + 1
                    findings[concern].append(
                        {"file": rpath, "line": line_no, "match": label}
                    )

    deps = read_deps(root, manifest_paths)

    # De-dup and cap each concern list for readability.
    def dedup(items, cap=60):
        seen = set()
        out = []
        for it in items:
            key = (it["file"], it["match"])
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
            if len(out) >= cap:
                break
        return out

    result = {
        "root": str(root),
        "files_scanned": file_count,
        "languages": sorted(languages) or ["unknown"],
        "manifests": [rel(root, m) for m in manifest_paths],
        "dependency_count": len(deps),
        "dependencies": deps,
        "entry_points": sorted(entry_points),
        "external_input_surfaces": dedup(findings["external_input"]),
        "sensitive_areas": {
            "auth": dedup(findings["auth"]),
            "secrets": dedup(findings["secrets"]),
            "database": dedup(findings["database"]),
            "side_effects": dedup(findings["side_effects"]),
        },
        "entry_point_signals": dedup(findings["entry_point"]),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    scan()
