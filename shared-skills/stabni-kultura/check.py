#!/usr/bin/env python3
"""Kontrola stábní kultury složek — jen čte, nic nemění.

Pravidla jsou popsaná v PRAVIDLA.md vedle tohoto souboru. Projekty = složky
aktuálního VS Code workspace, agendy a výjimky v projekty.json. Výstup je text (výchozí) nebo JSON (--json) pro skill.

Použití:
    python3 check.py                     # projekty aktuálního VS Code workspace
    python3 check.py --projekt springwalk
    python3 check.py --json --vse
"""
import argparse
import json
import os
import plistlib
import re
import subprocess
from pathlib import Path

_SKILL = Path(__file__).resolve().parent
REGISTR = _SKILL / "projekty.json"

# Složky, do kterých se nelezeme: závislosti, verzování, prostředí a zálohy
# (zálohy legitimně obsahují kopie čehokoli).
PRESKOCIT = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist",
    "build", ".pytest_cache", ".mypy_cache", "backup",
}
ZAKAZANE_PRIPONY = {
    ".py", ".pyc", ".sh", ".bash", ".zsh", ".command", ".js", ".mjs", ".cjs",
    ".ts", ".rb", ".pl", ".ps1", ".bat", ".log", ".db", ".sqlite",
    ".sqlite3", ".plist",
}
VYHRAZENE = ("todo.md", "roadmap.md")
# D1: datové soubory, jejichž jméno prozrazuje průběžně přepisovaný stav (ne statický dokument)
STAV_JMENO = re.compile(r"(progress|state|stav|cache|queue|fronta|seen|checkpoint|last[_-]?run|cursor|\.lock$|\.pid$)", re.I)
STAV_PRIPONY = {".json", ".jsonl", ".csv", ".tsv", ".txt", ".pid", ".lock", ".pkl"}
# D1: řetězcový literál s cestou do docs/ v kódu ("docs", "docs/…", "…/docs/…")
DOCS_LITERAL = re.compile(r"""["'](?:[^"'\n]*/)?docs(?:/[^"'\n]*)?["']""")
# D6: kód patří jen do src/, tyhle složky jsou jeho konkurenční místa
KONKURENCE_SRC = {"tools", "scripts"}
KOD_PRIPONY = {".py", ".sh"}
# D6: kód, který smí žít mimo src/ — skripty skillů a testy
D6_VYJIMKY = {"skills", "tests"}
# D4: statické dokumenty, které patří do docs/
DOKUMENTY = {".md", ".pdf", ".docx", ".doc", ".pages", ".odt", ".rtf", ".pptx", ".key", ".html", ".txt"}
# D4: soubory, které ze své podstaty žijí jinde než v docs/
META_SOUBORY = {"readme.md", "claude.md", "agents.md", "skill.md", "changelog.md", "license",
                "license.md", "requirements.txt", "robots.txt"}
# D4: složky, jejichž obsah do docs/ nepatří — kód/šablony/prompty a výstupy automatizací
# (ty by v docs/ porušily D1). Rozšiřuje se per projekt klíčem "vyjimky" v projekty.json.
D4_VYJIMKY = {"web", "site", "public", "static", "templates", "sablony", "prompty", "prompts",
              "skills", "styles", "src", "tests", "reports", "reporty", "digests", "prilohy",
              "logs", "data", "output", "state", "obsah", "tasks", "sablony-evolio", "automatizace"}
# D7: složka vzorů pro Evolio jedné agendy — pevná struktura, se kterou pracují skilly evolio-sablona*
SABLONY_EVOLIO = "sablony-evolio"
SE_KOREN_SOUBORY = {"workflow.md", "pravidla-agendy.md"}
SE_VZOR_JMENO = re.compile(r"^\d{2}-[a-z0-9-]+$")
SE_VZOR_POVINNE = {"zdroj.md", "mapovani-parametru.md"}
SE_VZOR_SLOZKY = {"predloha", "hotove", "hotove-stare", "revize"}
# D8: kostra právní agendy — povinné složky; src/ je volitelné (jen kde je kód, D6)
KOSTRA_AGENDY = ("backup", "docs", "automatizace", "sablony-evolio", "prompty")
KOSTRA_VOLITELNE = {"src"}
# D9: každá automatizace (podsložka automatizace/) má v kořeni tyhle čtyři soubory
AUTOMATIZACE = "automatizace"
AUTOMATIZACE_POVINNE = ("README.md", "roadmap.md", "todo.md", "workflow.md")


def rozbal(cesta: str) -> Path:
    return Path(os.path.expanduser(cesta))


def najdi_workspace(start: Path) -> Path:
    """První *.code-workspace v aktuální složce nebo v nadřazených."""
    for d in [start, *start.parents]:
        nalezene = sorted(d.glob("*.code-workspace"))
        if nalezene:
            return nalezene[0]
    raise SystemExit(f"Nenašel jsem žádný *.code-workspace od {start} nahoru — použij --workspace")


def nacti_projekty(workspace: Path) -> dict[Path, dict]:
    """Projekty = složky VS Code workspace; agendy a výjimky z projekty.json.

    Repo s nesouvisejícími projekty (klíče "kod" / "staticke" v projekty.json) se rozpadne
    na podprojekty: každý se kontroluje zvlášť a samotné repo jen jako kontejner (D10).
    """
    ws = json.loads(re.sub(r",(\s*[}\]])", r"\1", workspace.read_text(encoding="utf-8")))
    nastaveni = {rozbal(c).resolve(): n or {} for c, n in
                 json.loads(REGISTR.read_text(encoding="utf-8")).get("projekty", {}).items()}
    projekty: dict[Path, dict] = {}
    for f in ws.get("folders", []):
        p = (workspace.parent / os.path.expanduser(f["path"])).resolve()
        if not p.is_dir():
            continue
        n = nastaveni.get(p, {})
        zaklad = {"agendy": list(n.get("agendy", [])), "prvky": list(n.get("prvky", [])),
                  "vyjimky": list(n.get("vyjimky", [])), "repo": p, "rezim": "kod", "vnorene": set()}
        podprojekty = {p / c: r for r in ("kod", "staticke") for c in n.get(r, [])}
        if not podprojekty:
            projekty[p] = zaklad
            continue
        projekty[p] = {**zaklad, "rezim": "kontejner", "podprojekty": set(podprojekty),
                       "vyjimky_koren": list(n.get("vyjimky_koren", []))}
        for sp, rezim in podprojekty.items():
            projekty[sp] = {"agendy": [], "prvky": [], "vyjimky": [], "repo": p, "rezim": rezim,
                            "vnorene": {q for q in podprojekty if sp in q.parents}}
    return projekty


def projdi(koren: Path, vynechat: set[Path] = frozenset()):
    """os.walk s vynecháním PRESKOCIT, skrytých složek a vnořených podprojektů."""
    for dirpath, dirnames, filenames in os.walk(koren):
        dirnames[:] = [d for d in dirnames if d not in PRESKOCIT and not d.startswith(".")
                       and Path(dirpath) / d not in vynechat]
        yield Path(dirpath), filenames


def je_skript_nebo_log(nazev: str) -> bool:
    n = nazev.lower()
    return Path(n).suffix in ZAKAZANE_PRIPONY or ".log." in n


def nacti_automatizace() -> tuple[list[tuple[str, str]], list[tuple[str, Path]]]:
    """Projde launchd plisty a crontab.

    Vrací (cesty_do_docs, skripty): cesty_do_docs = (zdroj, cesta) míří přímo do docs/
    (program, pracovní adresář, log); skripty = (zdroj, soubor) pravidelně spouštěné skripty.
    """
    do_docs, skripty = [], []
    la = Path.home() / "Library" / "LaunchAgents"
    if la.is_dir():
        for plist in la.glob("*.plist"):
            try:
                data = plistlib.loads(plist.read_bytes())
            except Exception:
                continue
            zdroj = f"launchd {plist.name}"
            wd = data.get("WorkingDirectory")
            hodnoty = []
            for klic in ("ProgramArguments", "Program", "WorkingDirectory",
                         "StandardOutPath", "StandardErrorPath"):
                v = data.get(klic)
                hodnoty += v if isinstance(v, list) else [v] if v else []
            for v in hodnoty:
                if not isinstance(v, str):
                    continue
                if "/docs/" in v:
                    do_docs.append((zdroj, v))
                if v.endswith((".py", ".sh")):
                    f = Path(v) if os.path.isabs(v) else Path(wd or "/") / v
                    if f.is_file():
                        skripty.append((zdroj, f.resolve()))
    try:
        cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5).stdout
    except Exception:
        cron = ""
    for radek in cron.splitlines():
        if radek.lstrip().startswith("#"):
            continue
        if "/docs/" in radek:
            do_docs.append(("crontab", radek.strip()))
        for slovo in radek.split():
            if slovo.endswith((".py", ".sh")) and Path(slovo).is_file():
                skripty.append(("crontab", Path(slovo).resolve()))
    return do_docs, skripty


def kod_automatizace(skript: Path) -> list[Path]:
    """Kód, který pravidelně běží: skript, jeho sourozenci a podsložka src/."""
    soubory = [f for f in skript.parent.iterdir() if f.suffix in (".py", ".sh") and f.is_file()]
    if (skript.parent / "src").is_dir():
        soubory += [d / f for d, fs in projdi(skript.parent / "src") for f in fs if f.endswith(".py")]
    return soubory


def zkontroluj_kontejner(repo: Path, nast: dict) -> list[dict]:
    """D10: v repu s podprojekty smí být mimo podprojekty jen jejich nadřazené složky,
    meta soubory repa a výjimky z "vyjimky_koren"."""
    nalezy = []
    podprojekty = nast["podprojekty"]
    nadrazene = {a for sp in podprojekty for a in sp.parents if repo in a.parents or a == repo}
    vyjimky = {repo / v for v in nast["vyjimky_koren"]}
    fronta = [repo]
    while fronta:
        slozka = fronta.pop()
        for p in sorted(slozka.iterdir()):
            if p.name.startswith(".") or p in podprojekty or p in vyjimky or p.name in PRESKOCIT:
                continue
            rel = str(p.relative_to(repo))
            if p.is_dir() and p in nadrazene:
                fronta.append(p)
            elif p.is_dir():
                nalezy.append({"pravidlo": "D10", "cesta": rel, "co": "složka nepatří k žádnému podprojektu"})
            elif slozka != repo or Path(p.name.lower()).suffix in KOD_PRIPONY | DOKUMENTY - {".md"}:
                nalezy.append({"pravidlo": "D10", "cesta": rel, "co": "soubor mimo podprojekty"})
    return nalezy


def zkontroluj_staticky(projekt: Path, nast: dict) -> list[dict]:
    """Statický podprojekt: dokumenty smí ležet kdekoli, hlásí se jen kód, logy a databáze."""
    nalezy = []
    for slozka, soubory in projdi(projekt, nast["vnorene"]):
        for s in soubory:
            if not je_skript_nebo_log(s):
                continue
            cesta = str((slozka / s).relative_to(nast["repo"]))
            if "docs" in Path(cesta).parts:
                nalezy.append({"pravidlo": "D1", "cesta": cesta, "co": "skript / log / databáze v docs/"})
            elif Path(s.lower()).suffix in KOD_PRIPONY | {".js", ".mjs", ".ts"}:
                nalezy.append({"pravidlo": "D6", "cesta": cesta, "co": "kód ve statickém podprojektu"})
            else:
                nalezy.append({"pravidlo": "D1", "cesta": cesta, "co": "log / databáze ve statickém podprojektu"})
    return nalezy


def zkontroluj(projekt: Path, nast: dict, automatizace) -> list[dict]:
    if nast["rezim"] == "kontejner":
        return zkontroluj_kontejner(projekt, nast)
    if nast["rezim"] == "staticke":
        return zkontroluj_staticky(projekt, nast)
    nalezy = []
    vnorene = nast["vnorene"]
    agendy = nast["agendy"]
    vyjimky = D4_VYJIMKY | {v.lower() for v in nast["vyjimky"]}

    def nalez(pravidlo, cesta, co):
        koren = nast["repo"]
        rel = str(Path(cesta).relative_to(koren)) if str(cesta).startswith(str(koren)) else str(cesta)
        nalezy.append({"pravidlo": pravidlo, "cesta": rel, "co": co})

    # Jednotky = projekt + jeho agendy; jméno jednotky určuje projekt-<jméno>.md
    jednotky = [(projekt, projekt.name.lower())]
    for a in agendy + nast.get("prvky", []):
        jednotky.append((projekt / a, Path(a).name.lower()))

    povolene = set()
    for kde, jmeno in jednotky:
        if not kde.is_dir():
            nalez("D2", kde, "agenda z registru na disku neexistuje")
            continue
        docs = kde / "docs"
        for soubor in (f"projekt-{jmeno}.md", "roadmap.md", "todo.md"):
            povolene.add(docs / soubor)
        if not docs.is_dir():
            nalez("D2", docs, "chybí složka docs/")
        else:
            for soubor in (f"projekt-{jmeno}.md", "roadmap.md", "todo.md"):
                if not (docs / soubor).is_file():
                    nalez("D2", docs / soubor, "chybí povinný soubor")
        if not (kde / "backup").is_dir():
            nalez("D3", kde / "backup", "chybí složka backup/")

    # D9: automatizace/<název>/ má vlastní README, roadmap, todo a workflow (roadmap/todo tu nejsou porušení D2)
    for slozka, _ in projdi(projekt, vnorene):
        if slozka.name != AUTOMATIZACE:
            continue
        for a in sorted(slozka.iterdir()):
            if not a.is_dir() or a.name.startswith("."):
                continue
            for soubor in AUTOMATIZACE_POVINNE:
                povolene.add(a / soubor)
                if not (a / soubor).is_file():
                    nalez("D9", a / soubor, "chybí povinný soubor automatizace")

    koreny_docs = {kde / "docs" for kde, _ in jednotky}
    for slozka, soubory in projdi(projekt, vnorene):
        casti = slozka.relative_to(projekt).parts
        if casti and casti[-1].lower() in KONKURENCE_SRC and "src" not in casti:
            nalez("D6", slozka, f"složka {casti[-1]}/ — kód patří do src/")
        v_docs = "docs" in casti
        vyjmuto = any(c.lower() in vyjimky for c in casti)
        # src/<podprojekt>/docs/ smí mít vlastní roadmap/todo (malý projekt v src/ s vlastním výstupem)
        v_podprojektu = any(c == "src" and casti[i + 2:i + 3] == ("docs",) for i, c in enumerate(casti))
        for s in soubory:
            cesta = slozka / s
            if v_docs and je_skript_nebo_log(s):
                nalez("D1", cesta, "skript / log / databáze v docs/")
            elif v_docs and Path(s).suffix.lower() in STAV_PRIPONY and STAV_JMENO.search(s):
                nalez("D1", cesta, "stavový soubor v docs/ (jméno napovídá průběžný zápis) — ověř, kdo ho píše")
            nizke = s.lower()
            if (nizke in VYHRAZENE or (nizke.startswith("projekt-") and nizke.endswith(".md"))) \
                    and cesta not in povolene and not v_podprojektu:
                nalez("D2", cesta, "vyhrazený soubor mimo své místo (nebo špatné jméno)")
                continue
            if v_docs:
                if slozka in koreny_docs and cesta not in povolene and not s.startswith("."):
                    nalez("D5", cesta, "volně v kořeni docs/ — patří do podadresáře")
            elif (Path(nizke).suffix in DOKUMENTY and nizke not in META_SOUBORY
                  and not vyjmuto and not s.startswith(".")):
                nalez("D4", cesta, "statický dokument mimo docs/")
            # D6: kód mimo src/. Vstupní bod vedle vlastního src/ (main.py + src/) je v pořádku.
            if (not v_docs and Path(nizke).suffix in KOD_PRIPONY
                    and "src" not in casti and not any(c.lower() in D6_VYJIMKY for c in casti)
                    and not (slozka / "src").is_dir()):
                nalez("D6", cesta, "kód mimo src/")

    # D8: kostra právní agendy (backup, docs, automatizace, sablony-evolio, prompty/<prompt>/)
    for a in agendy:
        kde = projekt / a
        if not kde.is_dir():
            continue
        for slozka in KOSTRA_AGENDY:
            if not (kde / slozka).is_dir():
                nalez("D8", kde / slozka, "chybí složka kostry agendy")
        for p in kde.iterdir():
            if p.name.startswith(".") or p.name.lower() in META_SOUBORY:
                continue
            if p.is_file():
                nalez("D8", p, "soubor v kořeni agendy — patří do docs/ (nebo jiné složky kostry)")
            elif p.name not in KOSTRA_AGENDY and p.name not in KOSTRA_VOLITELNE:
                nalez("D8", p, "složka mimo kostru agendy (%s, volitelně src)" % ", ".join(KOSTRA_AGENDY))
        prompty = kde / "prompty"
        if prompty.is_dir():
            for p in prompty.iterdir():
                if not p.name.startswith(".") and p.is_file() and p.name.lower() not in META_SOUBORY:
                    nalez("D8", p, "v prompty/ jsou jen podadresáře pojmenované podle promptu")

    # D7: struktura sablony-evolio/ (kořen: dva .md + složky vzorů; vzor: zdroj, mapování, pracovní podsložky)
    for se, _ in projdi(projekt, vnorene):
        if se.name != SABLONY_EVOLIO:
            continue
        polozky = [p for p in se.iterdir() if not p.name.startswith(".")]
        for chybi in sorted(SE_KOREN_SOUBORY - {p.name for p in polozky if p.is_file()}):
            nalez("D7", se / chybi, "chybí povinný soubor složky vzorů")
        for p in polozky:
            if p.is_file() and p.name not in SE_KOREN_SOUBORY:
                nalez("D7", p, "v kořeni sablony-evolio/ smí být jen workflow.md a pravidla-agendy.md")
            elif p.is_dir() and not SE_VZOR_JMENO.match(p.name):
                nalez("D7", p, "složka vzoru se jmenuje NN-nazev (číslo, malá písmena, pomlčky)")
            elif p.is_dir():
                obsah = [q for q in p.iterdir() if not q.name.startswith(".")]
                for chybi in sorted(SE_VZOR_POVINNE - {q.name for q in obsah if q.is_file()}):
                    nalez("D7", p / chybi, "chybí povinný soubor vzoru")
                for q in obsah:
                    if q.is_dir() and q.name not in SE_VZOR_SLOZKY:
                        nalez("D7", q, "neznámá podsložka vzoru (povolené: %s)" % ", ".join(sorted(SE_VZOR_SLOZKY)))
                    elif q.is_file() and q.suffix.lower() not in {".md", ".docx"}:
                        nalez("D7", q, "ve složce vzoru jsou jen .md a .docx (zbytek do predloha/ nebo hotove/)")

    do_docs, skripty = automatizace
    for zdroj, cesta in do_docs:
        if any(cesta.startswith(str(v) + "/") for v in vnorene):
            continue
        if cesta.startswith(str(projekt) + "/") or (nast["repo"] == projekt and f"/{projekt.name}/" in cesta):
            nalez("D1", cesta, f"automatizace zapisuje / běží v docs/ ({zdroj})")
    videno = set()
    for zdroj, skript in skripty:
        if not str(skript).startswith(str(projekt) + "/") or any(v in skript.parents for v in vnorene):
            continue
        for f in kod_automatizace(skript):
            try:
                radky = f.read_text(encoding="utf-8", errors="ignore").splitlines()
            except OSError:
                continue
            for i, radek in enumerate(radky, 1):
                if DOCS_LITERAL.search(radek) and (f, i) not in videno:
                    videno.add((f, i))
                    nalez("D1", f"{f}:{i}", f"pravidelná automatizace ({zdroj}) pracuje s docs/ — ověř, jestli tam zapisuje: {radek.strip()[:90]}")
    return nalezy


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", help="cesta k *.code-workspace (výchozí: hledá se od aktuální složky nahoru)")
    ap.add_argument("--projekt", help="jen jeden projekt z workspace (jméno složky)")
    ap.add_argument("--json", action="store_true", help="výstup jako JSON")
    ap.add_argument("--vse", action="store_true", help="nezkracovat výpis nálezů")
    args = ap.parse_args()

    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else najdi_workspace(Path.cwd())
    projekty = nacti_projekty(workspace)
    if args.projekt:
        hledany = args.projekt.rstrip("/")
        projekty = {p: a for p, a in projekty.items()
                    if hledany in (p.name, a["repo"].name, str(p.relative_to(a["repo"])) if p != a["repo"] else "")
                    or str(p) == str(rozbal(hledany))}
        if not projekty:
            raise SystemExit(f"Projekt '{args.projekt}' není ve workspace {workspace}")

    automatizace = nacti_automatizace()
    vysledek = {str(p): zkontroluj(p, n, automatizace) for p, n in projekty.items()}

    if args.json:
        print(json.dumps({"workspace": str(workspace), "projekty": vysledek}, ensure_ascii=False, indent=2))
        return

    print(f"Workspace: {workspace}")
    limit = None if args.vse else 8
    celkem = 0
    for projekt, nalezy in vysledek.items():
        celkem += len(nalezy)
        stav = "✅" if not nalezy else f"❌ {len(nalezy)}"
        print(f"\n## {Path(projekt).name}  {stav}   ({projekt})")
        for pravidlo in ("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10"):
            pn = [n for n in nalezy if n["pravidlo"] == pravidlo]
            if not pn:
                continue
            print(f"  {pravidlo} ({len(pn)})")
            for n in pn[:limit]:
                print(f"    - {n['cesta']} — {n['co']}")
            if limit and len(pn) > limit:
                print(f"    … a dalších {len(pn) - limit} (--vse)")
    print(f"\nCelkem nálezů: {celkem} v {len(vysledek)} projektech (D4 = kandidáti, rozhoduje úsudek)")


if __name__ == "__main__":
    main()
