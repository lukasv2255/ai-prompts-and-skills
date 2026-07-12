# Mac — specifikace nasazení

> **Rozsah:** tento soubor popisuje **macOS**. Analogie k [WINDOWS.md](WINDOWS.md).
> **⚠ Stav: NEOVĚŘENO.** Tato specifikace popisuje **cílový stav (parita s Windows)**, ne odpozorovanou realitu — psáno z Windows stroje bez přístupu k Macu. Každý bod označený `TODO (ověřit)` je potřeba potvrdit přímo na Macu.
> **Pozn.:** v repu zatím **nejsou Mac install skripty** — existují jen `scripts/install-claude.ps1` a `scripts/install-codex.ps1` (Windows). Mac ekvivalenty (`.sh`) je potřeba doplnit, viz sekce na konci.

## Umístění repa

| | |
|---|---|
| Lokální cesta | `TODO (ověřit)` — Google Drive na Macu bývá `~/Library/CloudStorage/GoogleDrive-<email>/Můj disk/AI-prompts-and-skills` nebo `~/Google Drive/Můj disk/…` |
| Origin | `https://github.com/lukasv2255/ai-prompts-and-skills.git` |
| Aktivní větev | **`main`** |

Google Drive je druhá vrstva synchronizace navíc ke gitu. Zdroj pravdy je **git**.

## Rozdíl proti Windows: symlink místo junction

Windows používá **junction** (`New-Item -ItemType Junction`), protože nepotřebuje admin práva. Na Macu je nativní a bezproblémový **symlink** (`ln -s`). Funkčně ekvivalentní: obojí = živý odkaz na složku v repu.

## Mechanismus linkování — přehled per soubor (cílový stav)

Legenda:
- **Symlink (celá složka)** = živé, editace v repu je vidět okamžitě.
- **Symlink (per-skill)** = živé pro existující; **nový** skill potřebuje re-run install skriptu.
- **Kopie** = **NENÍ živé**; po editaci v repu nutný re-run install skriptu.

### Claude

| Zdroj v repu | Cíl na stroji | Typ | Propagace po editaci |
|---|---|---|---|
| `shared-skills/` | `~/.claude/skills` | **Symlink (celá složka)** | okamžitá — nový skill = jen přidat složku |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | **Kopie** `TODO (ověřit)` | re-run install skriptu |
| `claude/agents/code-reviewer.md` | `~/.claude/agents/code-reviewer.md` | **Kopie** | re-run install skriptu |
| `claude/hooks/check-project-structure.sh` | `~/.claude/hooks/check-project-structure.sh` | **Kopie** | re-run install skriptu |

> Pozn.: globální `claude/CLAUDE.md` předpokládá „zrcadlení přes symlink". Na Windows je to fakticky **kopie**. Na Macu `TODO (ověřit)` — jestli je symlink, propaguje se živě; jestli kopie, nutný re-run.

### Codex

| Zdroj v repu | Cíl na stroji | Typ | Propagace po editaci |
|---|---|---|---|
| `shared-skills/<name>` (každá složka) | `~/.agents/skills/<name>` | **Symlink (per-skill)** | existující živé; **nový skill = re-run** |
| `codex/AGENTS.md` | `~/.codex/AGENTS.md` | **Kopie** | re-run install skriptu |
| `codex/config.template.toml` | `~/.codex/config.toml` | **Kopie, jen pokud cíl chybí** | existující config se NEPŘEPÍŠE |

## Klíčová pravidla (stejná jako Windows)

1. **Skilly pro Claude** — jeden symlink celé složky. Nový skill = jen přidej složku do `shared-skills/`. Žádné ruční per-skill linkování.
2. **Skilly pro Codex** — per-skill symlinky. Nový skill se objeví až po re-runu install skriptu.
3. **`CLAUDE.md` a `AGENTS.md` jsou KOPIE** (na Windows ověřeno; na Macu `TODO`). Editace v repu se sama neprojeví.
4. Symlinky na Macu nepotřebují žádná speciální práva.
5. **Denní sync = git na větvi `main`:** `git pull origin main` / `git push origin main`.

## Setup na čistém Mac stroji (cílový, až budou `.sh` skripty)

```bash
git clone https://github.com/lukasv2255/ai-prompts-and-skills.git "<drive-path>/AI-prompts-and-skills"
cd "<drive-path>/AI-prompts-and-skills"
bash ./scripts/install-claude.sh   # TODO: skript zatím neexistuje
bash ./scripts/install-codex.sh    # TODO: skript zatím neexistuje
```

Dokud `.sh` skripty nejsou, ruční ekvivalent:

```bash
# Claude — symlink celé složky skillů
ln -sfn "<drive-path>/AI-prompts-and-skills/shared-skills" ~/.claude/skills
cp "<drive-path>/AI-prompts-and-skills/claude/CLAUDE.md" ~/.claude/CLAUDE.md

# Codex — per-skill symlinky
mkdir -p ~/.agents/skills
for d in "<drive-path>/AI-prompts-and-skills/shared-skills"/*/; do
  ln -sfn "$d" ~/.agents/skills/"$(basename "$d")"
done
cp "<drive-path>/AI-prompts-and-skills/codex/AGENTS.md" ~/.codex/AGENTS.md
```

## Po editaci — co je potřeba znovu spustit

| Co jsi změnil | Akce |
|---|---|
| Obsah existujícího skillu v `shared-skills/` | nic — živé přes symlink |
| **Nový** skill (nová složka) — pro Codex | re-run codex install (nebo `ln -s` nové složky) |
| `claude/CLAUDE.md` | re-run claude install (pokud je to kopie) |
| `claude/agents/*`, `claude/hooks/*` | re-run claude install |
| `codex/AGENTS.md` | re-run codex install |

## Co doověřit / doplnit na Macu

- [ ] Skutečná Drive cesta k repu na Macu.
- [ ] Je `~/.claude/skills` symlink celé složky, nebo per-skill? (Windows = celá složka.)
- [ ] Je `~/.claude/CLAUDE.md` symlink, nebo kopie? (Windows = kopie.)
- [ ] Jsou Codex junctiony/symlinky v `~/.agents/skills/` na aktuální Drive cestu? (Na Windows byly rozbité — mířily na starý klon.)
- [ ] Doplnit `scripts/install-claude.sh` a `scripts/install-codex.sh` jako `.sh` ekvivalenty PowerShell skriptů.
- [ ] Po ověření sjednotit znění globálního `claude/CLAUDE.md` na OS-neutrální invariant (přestat mluvit o ručních per-skill `ln -s`).
