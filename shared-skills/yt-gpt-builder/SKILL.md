---
name: yt-gpt-builder
description: >
  Tematická klasifikace YouTube transkriptů a příprava souborů pro OpenAI Assistant / GPT Store.
  GPT-4o-mini klasifikace do 15 témat, merge do souborů, upload do OpenAI Assistants API.

  Použij kdykoliv uživatel říká:
  - "klasifikuj transkripty podle tématu"
  - "připrav soubory pro OpenAI Assistant"
  - "chci dát transkripty do GPT"
  - "připrav knowledge base pro custom GPT"
  - "stav klasifikace" nebo dotaz na průběh klasifikace
---

# YT GPT Builder — klasifikace transkriptů pro OpenAI Assistant

Navazuje na skill `yt-transcripts`. Bere stažené transkripty a připraví je pro OpenAI Assistant.

Pipeline:
```
transcripts/*/*.txt
        ↓
  GPT-4o-mini klasifikace (1–2 témata per video)
        ↓
  topic_files/<téma>.txt  (max 15 souborů)
        ↓
  OpenAI Assistant (File Search)
        ↓
  GPT Store
```

---

## Požadavky

- Stažené transkripty ve složce `transcripts/` (viz skill `yt-transcripts`)
- `OPENAI_API_KEY` v `.env`
- `pip3 install openai python-dotenv`

---

## Spuštění

```bash
python3 build_topic_files.py >> classification.log 2>&1 &
```

Cena: ~$1–2 za 5000 transkriptů (GPT-4o-mini).

### Cron hlídač (Claude session)

Spusť CronCreate každých 5 minut s promptem:
```
Zkontroluj jestli běží build_topic_files.py — pokud ne, spusť ho znovu na pozadí.
```

---

## Stav klasifikace — formát odpovědi

Pokud uživatel napíše **"stav"** nebo se ptá na průběh klasifikace, spusť:

```bash
pgrep -f build_topic_files.py && echo "bezi" || echo "nespi"
python3 -c "import json; d=json.load(open('topic_classification.json')); print(f'Klasifikováno: {len(d)} / 5047')"
ls topic_files/*.txt 2>/dev/null | wc -l
```

### Formát reportu

📊 **Klasifikace**

`X / 5047 klasifikováno (Y%)` — běží ✅ / nespi ⚠️

Po dokončení vypsat počet videí per téma z `topic_files/`.

---

## Témata (15)

| Slug | Název |
|---|---|
| `protein_a_svalova_hmota` | Protein & svalová hmota |
| `hubnutí_a_metabolismus` | Hubnutí & metabolismus |
| `strevni_mikrobiom` | Střevní mikrobiom |
| `kardiovaskularni_zdravi` | Kardiovaskulární zdraví |
| `dlouhovekost_a_starnuti` | Dlouhověkost & stárnutí |
| `spanek_a_regenerace` | Spánek & regenerace |
| `vyziva_a_diety` | Výživa & diety |
| `cviceni_a_vykon` | Cvičení & výkon |
| `mozek_a_mentalni_zdravi` | Mozek & mentální zdraví |
| `hormony_a_metabolismus` | Hormony & metabolismus |
| `zanet_a_imunita` | Zánět & imunita |
| `vitaminy_a_suplementy` | Vitamíny & suplementy |
| `prevence_rakoviny` | Prevence rakoviny |
| `zeny_a_zdravi` | Ženy & zdraví |
| `ultra_prumyslove_potraviny` | Ultra-průmyslové potraviny |

---

## Výstup

```
topic_files/
├── protein_a_svalova_hmota.txt
├── strevni_mikrobiom.txt
└── ... (15 souborů)
```

Každý soubor: `## Název videa` + zdroj + text transkriptu, oddělené `---`.

---

## Soubory tohoto skillu

- `build_topic_files.py` — klasifikace + merge
