# Windows — specifikace nasazení

> **Rozsah:** tento soubor popisuje **výhradně Windows**. Mac ekvivalenty zatím nejsou ověřené — kde je Mac zmíněn, je to označeno jako `TODO (Mac)`.
> Účel: aby u **každého souboru** bylo jednoznačné, co je link (živé) a co kopie (nutný re-run), a kam se propaguje.

## Umístění repa

| | |
|---|---|
| Lokální cesta | `C:\Users\tommy\Můj disk\AI-prompts-and-skills` (Google Drive, streamovaný) |
| Origin | `https://github.com/lukasv2255/ai-prompts-and-skills.git` |
| Aktivní větev | **`main`** (README na některých místech uvádí `master` — to je zastaralé) |

Google Drive slouží jako druhá vrstva synchronizace navíc ke gitu. Zdroj pravdy je **git**.

## Mechanismus linkování — přehled per soubor

Legenda:
- **Junction (celá složka)** = živé, editace v repu je vidět okamžitě.
- **Junction (per-skill)** = živé pro existující; **nový** skill potřebuje re-run install skriptu, aby se založila jeho junction.
- **Kopie** = **NENÍ živé**; po editaci v repu musíš znovu spustit install skript, jinak se změna neprojeví.

### Claude — `scripts/install-claude.ps1`

| Zdroj v repu | Cíl na stroji | Typ | Propagace po editaci |
|---|---|---|---|
| `shared-skills/` | `~/.claude/skills` | **Junction (celá složka)** | okamžitá — nový skill = jen přidat složku, nic nelinkovat |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | **Kopie** | re-run `install-claude.ps1` |
| `claude/agents/code-reviewer.md` | `~/.claude/agents/code-reviewer.md` | **Kopie** | re-run `install-claude.ps1` |
| `claude/hooks/check-project-structure.sh` | `~/.claude/hooks/check-project-structure.sh` | **Kopie** | re-run `install-claude.ps1` |

### Codex — `scripts/install-codex.ps1`

| Zdroj v repu | Cíl na stroji | Typ | Propagace po editaci |
|---|---|---|---|
| `shared-skills/<name>` (každá složka) | `~/.agents/skills/<name>` | **Junction (per-skill)** | existující živé; **nový skill = re-run** `install-codex.ps1` |
| `codex/AGENTS.md` | `~/.codex/AGENTS.md` | **Kopie** | re-run `install-codex.ps1` |
| `codex/config.template.toml` | `~/.codex/config.toml` | **Kopie, jen pokud cíl chybí** | existující config se NEPŘEPÍŠE |

## Klíčová pravidla (past, na kterou se naráží)

1. **Skilly pro Claude** — jedna junction celé složky. Nový skill = jen přidej složku do `shared-skills/`. **Žádné ruční `ln -s` / `mklink` na jednotlivé skilly.**
2. **Skilly pro Codex** — per-skill junctiony. Nový skill se objeví až po re-runu `install-codex.ps1`.
3. **`CLAUDE.md` a `AGENTS.md` jsou KOPIE, ne linky.** Editace v repu se sama neprojeví — spusť příslušný install skript.
4. **Junctiony nepotřebují admin práva** (na rozdíl od symlinků) a fungují i na Drive-streamované cestě. Proto skripty používají `New-Item -ItemType Junction`, ne symlink.
5. **Denní sync = git na větvi `main`:** `git pull origin main` / `git push origin main`.

## Setup na čistém Windows stroji

```powershell
git clone https://github.com/lukasv2255/ai-prompts-and-skills.git "C:\Users\<username>\Můj disk\AI-prompts-and-skills"
cd "C:\Users\<username>\Můj disk\AI-prompts-and-skills"
powershell -ExecutionPolicy Bypass -File .\scripts\install-claude.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\install-codex.ps1
```

Skripty jsou idempotentní: existující junction přepíšou, nelinkovanou reálnou složku odsunou do `*.backup-<timestamp>`.

## Po editaci — co je potřeba znovu spustit

| Co jsi změnil | Akce |
|---|---|
| Cokoliv v `shared-skills/` (obsah existujícího skillu) | nic — živé přes junction |
| **Nový** skill (nová složka) — pro Codex | `install-codex.ps1` |
| `claude/CLAUDE.md` | `install-claude.ps1` |
| `claude/agents/*`, `claude/hooks/*` | `install-claude.ps1` |
| `codex/AGENTS.md` | `install-codex.ps1` |

## Nesoulady k dořešení (nezasahovat do sdílených souborů bez ověření Macu)

- **⚠ ROZBITÝ Codex (ověřeno 2026-07-12):** per-skill junctiony v `~/.agents/skills/` míří na `C:\Users\tommy\ai-prompts-and-skills\shared-skills\...` — starý klon, který už **neexistuje** (repo bylo přesunuto na Drive cestu, commit `0f12c7c`). Junctiony jsou mrtvé → Codex skilly nevidí.
  **Fix:** znovu spustit `install-codex.ps1` z aktuálního (Drive) repa — přelinkuje junctiony na správnou cestu.
- **README** v sekci *Daily Workflow* používá `master`; reálná větev je `main`.
- **`claude/CLAUDE.md`** (globální, sdílený s Macem) tvrdí:
  - „`~/.claude/skills/` obsahuje pouze symlinky na tuto složku“ → na Windows neplatí: Claude = **jedna junction celé složky**.
  - „při vytvoření nového skillu vždy vytvoř `ln -s …/NAZEV`“ → na Windows pro Claude **není potřeba**; pro Codex se to řeší re-runem `install-codex.ps1`, ne ručním `ln -s`.
  - Předpokládá, že se `~/.claude/CLAUDE.md` „zrcadlí přes symlink“ → na Windows je to **kopie**, zrcadlí se re-runem skriptu.
  Protože je tento soubor sdílený s Macem, oprava vyžaduje nejdřív ověřit, jak je nastaven Mac. `TODO (Mac)`.

## Mac — zatím neověřeno

`TODO (Mac):` zjistit, zda `~/.claude/skills` je whole-folder symlink (jako Windows junction) nebo per-skill, a jak se řeší `CLAUDE.md` (symlink vs kopie). Až bude ověřeno, sjednotit znění globálního `CLAUDE.md` na OS-neutrální invariant.
