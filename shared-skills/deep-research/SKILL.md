---
name: deep-research
description: >
  Deep research na firmu nebo na produkt. Cíl není shrnutí, ale pracovní kontext:
  jak to reálně funguje, jak se na tom vydělává, kde to drhne, co s tím mám udělat.
  Dva režimy — FIRMA (kam se hlásím: kalibrovaný úhel žádosti, ukázka práce, vizuál
  do značky firmy) a PRODUKT (softwarový nástroj: co umí, co stojí, co s daty,
  kde končí, čím ho nahradit).

  Použij kdykoliv uživatel říká:
  - "deep research na X" / "prozkoumej X" / "udělej mi rešerši na X"
  - "hlásím se do X, pochop jak dělají byznys"
  - "připrav mi podklad k žádosti do X"
  - "co umí <produkt>", "vyplatí se <produkt>", "srovnej <produkt> s ..."
  - "/deep-research X" (starší název: /company-research)

---

# deep-research — hluboká rešerše firmy nebo produktu

Cíl: pochopit věc tak, abych **nepsal a nerozhodoval do prázdna**.

Klíčové pravidlo celého skillu: **nejsi rešeršní papoušek.** Fakta oddělíš od domněnek,
čísla opřeš o zdroj a datum, a poctivě přiznáš, co nevíš. To je rozdíl mezi „AI výtahem"
a podkladem, který obstojí před skeptikem.

> **Poznámka: funguje i na produkt, ne jen na firmu.** Vyzkoušeno v praxi a funguje dobře —
> dotaz typu „deep research na Codexis AI" nebo „co reálně umí Slack" je legitimní vstup.
> Pro softwarové produkty platí jiné zdroje a jiná osnova, viz **Režim PRODUKT** níže.

---

## Vstup

- Jméno firmy / produktu + odkaz (web, inzerát, LinkedIn, dokumentace).
- **Režim.** Když to není zřejmé ze zadání, zeptej se — mění to celý výstup:
  - **FIRMA** → k čemu: AI-first role, nebo klasická (junior, wealth management, provoz…).
  - **PRODUKT** → k čemu: koupit/nahradit, integrovat, konkurovat, jít na schůzku s dodavatelem,
    nebo o tom psát.

---

# Režim FIRMA (žádost o práci / cold nabídka)

Metodika navazuje na `cv/sablona-zadosti.md` v projektu AI-brand (sekce B5–B10).

## 1. Sběr (WebSearch + WebFetch)

- Web firmy + inzerát → co prodává, komu, jak o tom mluví.
- **Rozhovory zakladatelů / tisk** — tady je reálná mechanika byznysu, ne homepage marketing.
  Hledej: „{firma} rozhovor strategie", „{zakladatel} {obor}", výroční zprávy, oborový tisk.
- Tým a jména (kdo rozhoduje, kdo je adresát), advisory board, mateřská/sesterská firma.
- Když je materiálu moc → scraping do Markdownu.

## 2. Syntéza — ne shrnutí, ale pracovní kontext

Sepiš `research.md` do složky žádosti (`cv/job-<slug>/research.md`) s těmito bloky:

- **Jak reálně dělají byznys** (ne jak to vypadá z homepage) — model, funnel, jak vydělávají.
- **Strategie / co dělají vs. co vědomě NEdělají** — druhé je často důležitější (viz níže).
- **Čísla — oddělená FAKTA vs. HYPOTÉZY.** Když si zdroje protiřečí, napiš to a označ „ověřit".
- **Tým a lidé** (adresát mailu).
- **Jejich moat** — ideálně jejich vlastními slovy z rozhovoru.
- **Přiznané mezery / rizika.**
- **Kam do toho sedím** (viz kalibrace).
- **Otevřené otázky před odesláním** (checklist).
- **Zdroje** (odkazy).

## 3. Kalibrace úhlu — NEJdůležitější krok

Podle typu role se zásadně liší, co s researchem uděláš:

- **AI-first role:** research → **prezentovaný výstup** (návrh zlepšení / příležitosti).
  Šířka (3–5 příležitostí s prioritou) NEBO hloubka (1 rozpracovaná). Nikdy dlouhý seznam bez priorit.
- **Klasická / seniorní / UHNWI role:** research je **skrytý nástroj, ne prezentovaný výstup.**
  Nevyžádaný „návrh, jak zlepšit vaše fungování" od juniora = přešlap. Úhel není
  „co děláte špatně", ale **„kde je ve vašem modelu mezera, do které sedím / co můžu odbavit"**
  — nabídka, ne kritika. AI drž jako tiché nářadí, ne jako pitch.

Nejsilnější nález bývá **„co firma vědomě NEdělá"** — když tvoje nabídka míří přesně
na věc, kterou neprodávají (protože si ji klient zařídí sám), je to slabá karta.
Otoč ji: ukaž, že to víš, a nabídni to, co jim reálně chybí.

## 4. (Volitelně) Důkaz místo tvrzení — ukázka práce

U rolí, kde jde o konkrétní dovednost, vyrob **malý reálný artefakt**, který tu dovednost
předvede (např. member-facing brief, due-diligence výtah, analýza). Struktura ukázky, která
dokazuje, že to není jen AI výtah:

- **Signál vs. šum** — vytáhni věc, co v titulku není vidět (rozpor v číslech, skryté riziko).
- **Oddělené fakta / můj odhad / co bych ověřil dál** — falsifikovatelnost.
- **Poznámka k metodě** — kde dělala AI (sběr, první třídění) a **kde rozhodoval člověk**
  (výběr signálu, interpretace, poctivé přiznání limitů). To je ta nedelegovatelná část.
- Čísla vždy se zdrojem a datem.

## 5. (Volitelně) Vizuál laděný do značky firmy

Když artefakt dostane HTML podobu: **odvoď design od značky firmy, ne z AI šablony.**
- Stáhni web firmy, vytáhni reálné tokeny: `curl` → grep na hex barvy a `font-family`.
- Postav self-contained HTML (Google Fonts, print styly pro PDF přes Cmd+P).
- AI-slop check: žádná nekonečná mřížka stejných karet, generické gradienty, zaměnitelný
  SaaS look. Barvy a typo musí mít vztah ke značce.
- Servíruj na localhostu (volný port mimo 8080–8089), pošli klikací odkaz. Nikdy `file://`.

## Výstupy režimu FIRMA

Ve složce `cv/job-<slug>/`:
- `research.md` — pochopení firmy (vždy).
- upravený `motivacni-dopis.txt` / `cv` na kalibrovaný úhel (když o to uživatel požádá).
- ukázka práce (`ukazka-*.md` / `.html`) — když role stojí na konkrétní dovednosti.

---

# Režim PRODUKT (softwarový nástroj — Codexis AI, Slack, …)

Rozdíl proti firmě: u produktu **nejde o to, kdo ho dělá, ale co reálně dělá, za kolik,
s jakými daty a kde končí.** Marketingová stránka je tu nejslabší zdroj — dokumentace,
ceník, changelog a stížnosti uživatelů jsou silnější.

## P1. Zdroje — v tomhle pořadí

1. **Dokumentace a API reference** — co produkt umí *technicky*. Co je v docs, existuje;
   co je jen na homepage, nemusí.
2. **Changelog / release notes / status page** — tempo vývoje a spolehlivost. Mrtvý changelog
   za rok je nález. Status page ukáže reálné výpadky, ne slibované SLA.
3. **Ceník** (+ `web.archive.org` na historii cen) — jak se cena škáluje, co je v jakém tieru,
   co je příplatek. Když ceník není veřejný, je to samo o sobě nález („enterprise sales").
4. **Reálné ceny u CZ produktů: registr smluv + profily zadavatelů.** U nástrojů, které
   kupuje veřejná správa nebo advokacie (typicky Codexis, ASPI, spisové služby), jsou tam
   skutečné částky a rozsahy licencí — to je tvrdší číslo než jakýkoliv ceník.
5. **Recenze s datem** — G2, Capterra, Reddit, Hacker News, oborová fóra. Nefiltruj podle
   hvězdiček, ale podle **konkrétnosti stížnosti**. Recenze bez data zahoď.
6. **Konkurence a čím se vymezuje** — s kým se produkt srovnává na vlastním webu, a hlavně
   s kým ne.

**Vyzkoušej to sám, pokud existuje trial nebo free tier.** Třicet minut vlastního testu
překoná deset recenzí. Zapiš, co nešlo a kde jsi narazil na limit — to v žádném článku není.

## P2. Osnova `research.md` pro produkt

- **Jakou práci produkt odbavuje** (jobs-to-be-done) a komu — ne seznam featur.
- **Co je GA vs. beta vs. roadmapa.** Každé tvrzení s **datem a verzí** — software se mění
  a rešerše bez data je za půl roku nepoužitelná.
- **Cena a jak se škáluje** — per seat / per usage / per dokument, minimální závazek,
  co dělá cena při 5 vs. 50 uživatelích.
- **Data: kde běží, kdo je vidí, co se s nimi děje.** Hosting (EU/US), GDPR, zpracovatelská
  smlouva, retence.
- **Integrace a API** — dá se to napojit, nebo je to uzavřená krabice? Export dat = jak
  vypadá odchod (lock-in).
- **Kde produkt končí** — limity, které se v marketingu nepíšou (počet dokumentů, velikost
  souboru, jazyky, rychlost, chybějící role a práva).
- **Alternativy** — 2–4 s jednou větou, proč by člověk vzal je.
- **Fakta vs. hypotézy vs. co ověřit u dodavatele.**
- **Zdroje s datem stažení.**

## P3. Navíc u AI produktů (Codexis AI a spol.)

Tady se nejvíc lže marketingem, takže cíleně rozliš:

- **Co je LLM a co obyčejná rule-based logika / fulltext.** Často je „AI" jen našroubovaná
  na starý vyhledávač.
- **Nad čím to běží** — uzavřená kurátorovaná báze (judikatura, legislativa), nebo otevřený web?
  U právních nástrojů je uzavřená báze ta hodnota.
- **Cituje zdroje u každé odpovědi?** Bez dohledatelné citace je výstup v právu nepoužitelný.
- **Co dělá s halucinacemi** — přiznává nejistotu, nebo si vymýšlí s jistotou?
- **Trénuje se na mých datech?** Opt-out, nebo je to v podmínkách natvrdo?
- **Kde je člověk v procesu** — co nástroj rozhodne sám a co jen předloží ke schválení.
- **Jaký model pod kapotou a čí** (vlastní / OpenAI / Anthropic / open-weights) a co to znamená
  pro cenu, latenci a odesílání dat mimo EU.

## P4. Kalibrace výstupu podle toho, proč se ptám

- **Koupit / nahradit** → rozhodovací tabulka: co získám, co ztratím, cena za rok, co ověřit
  na demu. Jedno doporučení, ne pět možností.
- **Integrovat** → důraz na API, limity, autentizaci, export.
- **Konkurovat / psát o tom** → kde produkt vědomě nejde a proč, tam je díra.
- **Jdu na schůzku s dodavatelem** → **seznam nepříjemných otázek**, na které ceník ani
  homepage neodpovídají. Tohle je často nejcennější výstup celé rešerše.

## Výstupy režimu PRODUKT

- `research-<produkt>.md` — osnova P2 (vždy).
- Rozhodovací tabulka nebo seznam otázek na dodavatele — podle kalibrace P4.
- HTML report (skill `report`) — když to má jít někomu ukázat.

---

## Anti-vzory (oba režimy)

- Shrnutí místo pracovního kontextu.
- Čísla bez zdroje, bez data, nebo bez oddělení fakt/hypotéza.
- Nevyžádaný „návrh na zlepšení" u klasické/seniorní role.
- HTML z generické šablony bez vztahu ke značce.
- Nabízet firmě věc, kterou vědomě neprodává.
- **U produktu:** převyprávěná pricing page a homepage jako hlavní zdroj.
- **U produktu:** srovnávací „top 10 nástrojů" články — je to affiliate SEO, ne rešerše.
- **U produktu:** rešerše bez data a verze — za půl roku je to jen dohad.
