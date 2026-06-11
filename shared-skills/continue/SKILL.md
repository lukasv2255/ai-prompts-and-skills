---
name: continue
description: Navrhne prompt pro pokračování práce v nové session. Použij když uživatel říká "ukončujeme", "continue", "připrav handoff", nebo končíme delší práci a chceme pokračovat v nové session.
allowed-tools: Bash, Read, Grep, Glob
---

# /continue — handoff do nové session

Budu pokračovat v nové session. Navrhni prompt, jak tam navázat.

**Nic neukládej** — žádné commity, žádné zápisy do paměti (`tasks/`, `docs/`,
auto-memory). Jen vypiš handoff prompt.

Zjisti si aktuální branch (`git branch --show-current`) a stav rozdělané práce.
Pak vypiš prompt v **jednom ` ``` ` bloku**, aby šel vložit jedním copy-paste do
nové session. Musí obsahovat:

- **Název projektu + aktuální branch**
- **3–5 vět:** co se v této session udělalo a proč (nezacházej do detailů)
- **Odkazy na kontext** — soubory, které nová session musí přečíst:
  `CLAUDE.md`, `tasks/todo.md` (pokud existují) + 1–3 soubory klíčové pro rozdělaný úkol
- **Číslovaný seznam dalších kroků** — co zbylo nedodělané, nebo co následuje
- **Sekce „Nedělej"** — co nová session nesmí (např. měnit stavy v DB,
  odesílat maily, pouštět deploy, pushovat na main). Odvoď z kontextu session.

### Styl promptu

- Česky, stručně, **max ~25 řádků**
- Imperativ („přečti", „spusť", „nezapomeň")
- Konkrétní cesty a příkazy (ne „nějak otestuj")

### Argumenty

Pokud uživatel za příkazem napsal argumenty (`/continue zaměření na X`),
ber je jako zaměření příští session a promítni do dalších kroků.
