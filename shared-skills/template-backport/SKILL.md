---
name: template-backport
description: Přenese fix z klientské instance do template repozitáře přes cherry-pick. Použij kdykoliv uživatel říká "přenes opravu do template", "backport do vzoru", "portuj fix", nebo když je oprava hotová v klientovi a má jít do template.
---

# Template Backport

Přenese konkrétní commit (fix/opravu) z klientské instance projektu zpět do template repozitáře.

## Kdy použít

- Oprava byla nalezena a commitnuta v klientské instanci
- Ta samá oprava má jít do template, aby ji dostaly i budoucí instance
- Commit obsahuje mix kódové opravy + klientsky specifické soubory (lessons.md, .env.example atp.)

## Postup

### KROK 1 — Zjisti hash commitu s opravou

```bash
# v klientském repozitáři
git log --oneline -10
```

Poznamenej hash commitu (např. `76895fb`).

### KROK 2 — Zjisti cestu k template repozitáři

Zeptej se uživatele, nebo hledej v `~/claude-code/` a `~/Můj disk/`:

```bash
find ~ -name "CLAUDE.md" -path "*/mail-agent*" 2>/dev/null | head -5
```

### KROK 3 — Přejdi do template a přidej klienta jako dočasný remote

```bash
cd <TEMPLATE_PATH>
git remote add client <CLIENT_REPO_URL>   # z: git remote get-url origin (v klientovi)
git fetch client main
```

### KROK 4 — Cherry-pick commitu

```bash
git cherry-pick <COMMIT_HASH>
```

### KROK 5 — Vyřeš konflikty (pokud vznikly)

Template a klient se časem rozchází — konflikty jsou normální.

**Pravidlo rozlišení:**

- Kódové soubory (`src/`) → zachovej template verzi + přidej pouze změnu z opravy
- Dokumentace specifická pro klienta (`tasks/lessons.md`, `docs/`) → resetuj na template verzi:

```bash
git checkout HEAD -- tasks/lessons.md
# nebo pro celou složku:
git checkout HEAD -- docs/
```

- Po vyřešení všech konfliktů:

```bash
git add src/modules/opraveny_soubor.py
git cherry-pick --continue --no-edit
```

### KROK 6 — Ověř syntaxi a smaž dočasný remote

```bash
python3 -m py_compile src/modules/opraveny_soubor.py && echo "OK"
git remote remove client
```

### KROK 7 — Push do template

```bash
git push
```

### KROK 8 — Ověř výsledek

```bash
git log --oneline -3
git show HEAD -- src/modules/opraveny_soubor.py | grep <klicove_slovo_opravy>
```

## Poznámky

- `git cherry-pick` potřebuje commit dostupný v aktuálním repozitáři — proto dočasný remote
- Po cherry-picku remote vždy odstraň: `git remote remove client`
- Uncommitted změny v template nevadí, pokud se netýkají stejných souborů jako oprava
- Pokud template obsahuje pokročilejší verzi opravovaného kódu (refactor, nové funkce), **zachovej template verzi** a přidej jen podstatu opravy (např. `timeout=30` parametr)

## Správný long-term workflow

Správné pořadí je **template → klient**, ne naopak:

1. Oprav template
2. V klientovi: `git fetch upstream && git merge upstream/main`

Backport (klient → template) je záchranný postup pro situace, kdy byl bug nalezen v klientovi dřív. Ideálně se mu vyhni disciplínou: opravy sdíleného kódu vždy dělej v template.
