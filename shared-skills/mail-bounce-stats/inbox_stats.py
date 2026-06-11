"""
Inbox stats — bounce/reject klasifikace pro libovolnou mail-agent instanci.

count_bounce_stats(): počet HARD rejected + soft bounces napříč CELOU IMAP
schránkou. Použij v CRM/Stats dashboardu pro odhad "kolik leadů je mrtvých"
vs "kolik dočasně nelze doručit".

Pipeline:
1. Najdi bounce kandidáty přes FROM "MAILER-DAEMON" / "postmaster" (RFC 5321).
2. Pro každý FETCH BODY.PEEK[] a parsuj DSN `Status:` (RFC 3464).
3. Klasifikuj:
     hard   = Status 5.1.x (bad address) / 5.7.x (policy/blocked)
              NEBO generický 5.x.x bez textu o full/quota
              → adresa permanentně mrtvá nebo blokuje
     soft   = Status 4.x.x (temp)
              NEBO Status 5.2.2 (mailbox full)
              NEBO 5.x.x s textem o plné schránce/quotě (CZ i EN)
              → lead pořád žije, jen teď nelze doručit
     none   = bez DSN Status (DMARC reporty, auto-maily) → nezapočítané

Skenuje všechny IMAP složky kromě označených \\Sent, \\Drafts, \\Trash,
\\Junk, \\All, \\Noselect. Celkový "sent" se počítá ze složky \\Sent.

Závislost: tento modul očekává funkci `load_credentials_or_env()` v modulu
`src.imap_credentials_store` (mail-agent template). Vrací objekt s atributy
`imap_host`, `imap_port`, `imap_user`, `imap_password`. Pokud tvoje
instance má credentials jinde, uprav `_connect_imap()` níže.
"""
from __future__ import annotations

import imaplib
import logging
import re
import ssl

from src.imap_credentials_store import load_credentials_or_env

logger = logging.getLogger(__name__)

# Bounce odesílatelé (RFC 5321 — MTA vrací nedoručené přes tyto adresy).
BOUNCE_FROM_PATTERNS = ("MAILER-DAEMON", "postmaster")

# DSN Status (RFC 3464): "Status: X.Y.Z" v těle bounce mailu.
_STATUS_RE = re.compile(r"^Status:\s*(\d)\.(\d+)\.(\d+)", re.MULTILINE | re.IGNORECASE)

# Klíčová slova pro "soft" důvod v těle bouncu — i když je Status 5.x.x,
# bývá to jen generický kód kolem skutečně dočasného důvodu (typicky plná schránka).
_SOFT_BODY_PATTERNS = re.compile(
    r"(mailbox[^\n]{0,80}?(?:is\s+)?full"
    r"|mailbox[^\n]{0,80}?over[\s_-]*quota"
    r"|over[\s_-]*quota|quota\s+exceeded|exceeded\s+(?:storage\s+)?quota"
    r"|not\s+enough\s+disk\s+quota|disk\s+quota|insufficient\s+(?:disk|storage)"
    r"|pln[áa]\s+schr[áa]nka|p[rř]ekro[čc]en[ao]\s+kv[oó]ta)",
    re.IGNORECASE,
)

# Atributy IMAP LIST složek, které do bounce scanu nepatří.
_SKIP_ATTRS = {"\\Sent", "\\Drafts", "\\Trash", "\\Junk", "\\All", "\\Noselect"}

# IMAP LIST řádek: (\Flag1 \Flag2) "/" "FolderName"
_LIST_RE = re.compile(
    r'^\((?P<attrs>[^)]*)\)\s+(?P<delim>"[^"]*"|NIL)\s+(?P<name>"(?:[^"\\]|\\.)*"|\S+)$'
)


def _connect_imap() -> imaplib.IMAP4_SSL:
    """TLS 1.2 IMAP login. Konzervativní pin proti shakyho TLS 1.3 stackům."""
    creds = load_credentials_or_env()
    ctx = ssl.create_default_context()
    try:
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        ctx.maximum_version = ssl.TLSVersion.TLSv1_2
    except Exception:
        pass
    conn = imaplib.IMAP4_SSL(creds.imap_host, creds.imap_port, ssl_context=ctx)
    conn.login(creds.imap_user, creds.imap_password)
    return conn


def _parse_list_line(line) -> tuple[set[str], str] | None:
    s = line.decode("utf-8", errors="replace") if isinstance(line, (bytes, bytearray)) else str(line)
    m = _LIST_RE.match(s.strip())
    if not m:
        return None
    attrs = set(m.group("attrs").split())
    name = m.group("name")
    if name.startswith('"') and name.endswith('"'):
        name = name[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return attrs, name


def _list_scannable_folders(conn) -> list[str]:
    typ, data = conn.list()
    if typ != "OK" or not data:
        return []
    out: list[str] = []
    for raw in data:
        parsed = _parse_list_line(raw)
        if not parsed:
            continue
        attrs, name = parsed
        if attrs & _SKIP_ATTRS:
            continue
        out.append(name)
    return out


def _list_sent_folders(conn) -> list[str]:
    typ, data = conn.list()
    if typ != "OK" or not data:
        return []
    out: list[str] = []
    for raw in data:
        parsed = _parse_list_line(raw)
        if not parsed:
            continue
        attrs, name = parsed
        if "\\Sent" in attrs and "\\Noselect" not in attrs:
            out.append(name)
    return out


def _classify_bounce(conn, uid: bytes) -> str:
    """Vrátí 'hard' / 'soft' / 'none'. BODY.PEEK[] nemění \\Seen flag."""
    typ, data = conn.uid("FETCH", uid, "(BODY.PEEK[])")
    if typ != "OK" or not data:
        return "none"
    text = ""
    for part in data:
        if isinstance(part, tuple) and len(part) >= 2 and isinstance(part[1], (bytes, bytearray)):
            try:
                text = part[1].decode("utf-8", errors="replace")
            except Exception:
                text = part[1].decode("latin-1", errors="replace")
            break
    if not text:
        return "none"

    m = _STATUS_RE.search(text)
    if not m:
        return "none"
    cls, sub, detail = m.group(1), m.group(2), m.group(3)

    if cls == "4":
        return "soft"
    if cls != "5":
        return "none"

    if sub == "1" or sub == "7":
        return "hard"
    if sub == "2" and detail == "2":  # 5.2.2 mailbox full
        return "soft"
    if _SOFT_BODY_PATTERNS.search(text):
        return "soft"
    return "hard"


def _count_messages(conn, folder: str) -> int:
    quoted = f'"{folder}"' if not (folder.startswith('"') and folder.endswith('"')) else folder
    result, _ = conn.select(quoted, readonly=True)
    if result != "OK":
        return 0
    typ, data = conn.uid("SEARCH", None, "ALL")
    if typ != "OK" or not data or not data[0]:
        return 0
    return len(data[0].split())


def count_bounce_stats() -> dict:
    """Vrátí dict s klíči: rejected (hard), soft_bounces, bounces_total,
    sent_total, folders, per_folder, sent_folders, error."""
    empty = {
        "rejected": 0,
        "soft_bounces": 0,
        "bounces_total": 0,
        "sent_total": 0,
        "folders": [],
        "per_folder": {},
        "sent_folders": [],
    }
    try:
        load_credentials_or_env()
    except Exception as exc:
        return {**empty, "error": f"IMAP creds: {exc}"}

    try:
        conn = _connect_imap()
    except Exception as exc:
        return {**empty, "error": f"IMAP connect: {exc}"}

    per_folder: dict[str, int] = {}
    rejected_total = 0
    soft_total = 0
    sent_total = 0
    sent_folders: list[str] = []
    try:
        for folder in _list_scannable_folders(conn):
            quoted = f'"{folder}"' if not (folder.startswith('"') and folder.endswith('"')) else folder
            result, _ = conn.select(quoted, readonly=True)
            if result != "OK":
                logger.debug(f"[inbox_stats] složka {folder} nedostupná")
                continue
            candidate_uids: set[bytes] = set()
            for pattern in BOUNCE_FROM_PATTERNS:
                typ, data = conn.uid("SEARCH", None, "FROM", f'"{pattern}"')
                if typ == "OK" and data and data[0]:
                    candidate_uids.update(data[0].split())
            hard_in_folder = 0
            for uid in candidate_uids:
                kind = _classify_bounce(conn, uid)
                if kind == "hard":
                    hard_in_folder += 1
                elif kind == "soft":
                    soft_total += 1
            per_folder[folder] = hard_in_folder
            rejected_total += hard_in_folder

        sent_folders = _list_sent_folders(conn)
        for folder in sent_folders:
            sent_total += _count_messages(conn, folder)
    finally:
        try:
            conn.logout()
        except Exception:
            pass

    return {
        "rejected": rejected_total,
        "soft_bounces": soft_total,
        "bounces_total": rejected_total + soft_total,
        "sent_total": sent_total,
        "folders": list(per_folder.keys()),
        "per_folder": per_folder,
        "sent_folders": sent_folders,
        "error": None,
    }


# Alias pro zpětnou kompatibilitu, pokud někdo importuje starý název.
count_rejected_subjects = count_bounce_stats


if __name__ == "__main__":
    # Rychlý test z příkazové řádky: `python -m src.modules.inbox_stats`
    import json
    print(json.dumps(count_bounce_stats(), ensure_ascii=False, indent=2))
