# Brand kity (přepínač)

Každý soubor `brands/<slug>.css` je jedna značka — sada design tokenů v `:root`.
Skill při stavbě reportu vloží obsah zvoleného souboru mezi značky
`/* BRAND:START */` a `/* BRAND:END */` v `template.html`.

- `ai-brand.css` — výchozí editorial paleta projektu AI-brand.
- `springwalk.css` — paleta advokátní kanceláře Spring Walk (oranžová #de492a + námořní modrá #193a5c).

## Přidat značku příjemce

1. Zkopíruj `ai-brand.css` na `brands/<slug>.css`.
2. Přepiš barvy podle webu/značky příjemce (`--bg`, `--surface`, `--primary`,
   `--accent`, `--sidebar`…). `--sidebar` je tmavá barva bočního panelu,
   `--sidebar-text` světlý text v něm.
3. Fonty: `--font-head` / `--font-body` / `--font-mono`. Když značka používá jiné
   Google Fonts než výchozí, přidej do template `<head>` i jejich `<link>`.

Použití: `/report <zdroj> --brand <slug>` (bez přepínače = `ai-brand`).
