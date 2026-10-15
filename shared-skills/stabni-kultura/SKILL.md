---
name: stabni-kultura
description: >
  Zkontroluje stábní kulturu složek v projektech aktuálního VS Code workspace podle
  pravidel v PRAVIDLA.md (docs/ jen statické, povinné projekt-<jméno>.md / roadmap.md /
  todo.md, backup/ v každém projektu a agendě, statické soubory v docs/ s podadresáři, kód jen v src/).
  Upozorňuje na porušení a ke každému dává dva návrhy opravy; přesune až po výslovném
  potvrzení konkrétního návrhu. Nic nemaže.
  Použij kdykoliv uživatel říká: "zkontroluj stábní kulturu", "je tu pořádek ve složkách?",
  "dodržuju pravidla složek?", "kde porušuju strukturu", "/stabni-kultura [projekt]".
---

# Stábní kultura složek

Pravidla: `PRAVIDLA.md` (vedle tohoto souboru). Agendy a výjimky: `projekty.json`.
Které projekty se kontrolují, určuje VS Code workspace (`*.code-workspace`), který se
najde od aktuální složky nahoru.

## Postup

1. Spusť kontrolu (cesta ke skriptu je složka tohoto skillu):
   ```
   python3 <skill>/check.py --json --vse [--projekt <jméno>]
   ```
2. **D1–D3, D5** jsou deterministické — převezmi je, jak jsou.
3. **D4 posuď úsudkem.** Kandidáty seskup po složkách a u každé skupiny rozhodni:
   - *přesunout* → navrhni cílový podadresář v `docs/` (tematický, klidně s jedním souborem),
   - *nechat* → složka je funkční součást kódu/šablon/výstupu (např. vstup agenta,
     předloha pro generování); navrhni ji do `"vyjimky"` v `projekty.json`.
4. U **D1** zjisti, jestli skript/log patří k běžící automatizaci (launchd, cron,
   watchdog). Nálezy „stavový soubor“ a „pravidelná automatizace pracuje s docs/“ jsou
   kandidáti: přečti kód a rozhodni, jestli do `docs/` **zapisuje** (= porušení), nebo
   jen čte (= v pořádku, do reportu jen jedním řádkem „ověřeno, jen čte“). Taková položka je nejvážnější; návrh = přesunout kód do `src/<téma>/`
   (živý) nebo `src/archiv/<téma>/` (vyřazený) a přenastavit cestu v automatizaci.
   **Nikdy nenavrhuj přesun do `backup/`** — ten je jen na zálohy před velkou změnou.
5. Report vypiš po projektech; nálezy seskup po složkách a každou skupinu očísluj:
   pravidlo → cesta → co je špatně → **návrh A** a **návrh B** (dvě alternativy,
   např. „přesunout do `tools/`“ / „přidat složku do výjimek“). U návrhu přesunu uveď,
   co by se muselo změnit s ním (odkazy na starou cestu v kódu, launchd plistech,
   CLAUDE.md / AGENTS.md) a jestli položka patří k něčemu, co právě běží.
   Pořadí: D1 s automatizací, D2/D3, D5, D6, D7, D8, D9, nakonec D4. Souhrn s počty na začátku.
6. Skonči a čekej. Nic neprováděj, dokud uživatel nepotvrdí konkrétní návrh
   číslem a písmenem (např. „3A“, „1B a 2A“). Holé „y“ bez čísel nestačí — zeptej se, které.

## Po potvrzení: jen přesun

- Proveď **jen potvrzené návrhy**, po jedné skupině; po každé spusť `check.py` znovu.
- **Jediná povolená akce je přesun** (`git mv`, je-li soubor v gitu, jinak `mv`) a s ním
  úprava odkazů na starou cestu (kód, launchd plisty, CLAUDE.md / AGENTS.md) ve stejném kroku.
- **Nikdy nemaž** a nic nepřepisuj — když v cíli soubor už existuje, zastav se a zeptej se.
- Nesahej na nic, co právě běží (launchd agent, kampaň, watchdog) — upozorni a nepřesouvej.
- Zakládání chybějících souborů a složek (D2, D3) a změny v `projekty.json` jsou jen návrhy;
  proveď je jen na výslovný pokyn k té konkrétní věci.
