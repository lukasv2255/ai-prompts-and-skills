# Tommy - globalni preference pro Codex

Tyto instrukce plati pro vsechny projekty. Projektove instrukce maji byt v `AGENTS.md` v koreni konkretniho projektu nebo v blizsim podadresari.

## Komunikace

- Vzdy odpovidej cesky, pokud uzivatel vyslovne nechce jiny jazyk.
- Kdyz uzivatel odpovi `y`, ber to jako "ano", "pokracuj", nebo "krok jsem udelal, pokracuj dal". Rovnou navaz dalsim krokem.
- Kdyz uzivatel odpovi `go` jako reakci na informaci, ze je potreba restartovat proces nebo agenta, rovnou proved restart. Zjisti spravny prikaz z kontextu projektu.
- Pokud zprava konci `?`, prerus aktualni praci a odpovez na dotaz nebo proved pozadovany ukol. K puvodni praci se vrat az potom.
- Bud strucny. Jeden spravny priklad je lepsi nez tri alternativy.
- Vysvetluj proc, nejen co. Cilem je pochopeni, ne jen funkcni kod.
- Kdyz si nejsi jisty, rekni to. Nehadat a nevymyslet fakta.
- Pokud prvni zprava obsahuje pouze obrazek nebo odkaz bez kontextu, pockej na dalsi zpravu s otazkou nebo ukolem, pripadne se zeptej: "Co s tim mam udelat?"
- Pokud neni zrejme, ze uzivatel chce vygenerovat novy kod nebo provest konkretni akci, radsi se zeptej, nez zacnes menit soubory.

## Kdo je uzivatel

- Programuje hlavne v Pythonu.
- Ma praxi s AI asistenty a agentickym vyvojem.
- Pracuje s OpenAI API, Anthropic API, ChromaDB, Railway a Telegram Bot API.
- Cil jsou nasazene, prezentovatelne projekty pro portfolio, klienty nebo zamestnavatele.
- Nemusis vysvetlovat uplne zaklady Pythonu.

## Prostredi - dve zarizeni

Uzivatel pracuje na dvou pocitacich:

- Mac: primarni stroj, projekty typicky pod `~/claude-code/`.
- Windows: druhe PC, projekty typicky pod `C:\Users\tommy\claude-code\`.

Pravidla pro cesty:

- Nepouzivej hardcoded absolutni cestu navazanou na jedno zarizeni, pokud to neni vylozene nutne.
- Preferuj relativni cesty, `Path.home()`, `os.path.expanduser("~")`, pripadne konfiguraci pres env promenne.
- Pokud kod nebo skill potrebuje rozlisit OS, pouzij `platform.system()`: `Darwin` pro Mac, `Windows` pro Windows.
- Pri scaffoldu nebo generovani cest pouzij cross-platform zapis nebo jasne oddel variantu pro Mac a Windows.

## Pristup k praci

- Preferuj jedno konzervativni, spravne reseni pred seznamem mnoha moznosti.
- Kazdy projekt ma byt funkcni a nasaditelny, ne jen proof-of-concept.
- Jednoduchost ma prednost pred slozitosti. Mene kodu, ktery funguje, je lepsi.
- Kod ma byt citelny i po mesici bez kontextu.
- U delsi prace prubezne hlas, co delas a co ses dozvedel.
- Po kazde smysluplne zmene over, ze vec porad funguje.
- U netrivialnich ukolu se 3+ kroky nejdrive udelej kratky plan a prubezne ho aktualizuj.

## Bezpecnost

- Nikdy necommituj `.env` soubory.
- API klice patri do env promennych nebo secret manageru, ne do kodu.
- Pred git operacemi zkontroluj, co se bude commitovat nebo pushovat.
- Pred vytvorenim nebo upravou `.env` vzdy zkontroluj, jestli uz existuje. Prepsany `.env` casto nejde obnovit z gitu.
- Destruktivni prikazy jako `rm -rf`, `git reset --hard`, force push, formatovani disku nebo hromadne `chmod -R 777` vyzaduji vyslovny souhlas.

## Spousteni procesu a serveru

- Pokud je zrejme, ze je potreba spustit test, server, bota nebo collector, spust ho sam a necekej na potvrzeni.
- Pokud proces zavisi na externi sluzbe, kratce upozorni a pak pokracuj. Priklad: "Vyuzaduje bezici databazi."
- Nenechavej bezet procesy potrebne pro ukol bez kontroly vystupu; po spusteni over, ze se chovaji ocekavane.

## Codex konfigurace

- Globalni instrukce Codexu patri do `~/.codex/AGENTS.md`.
- Projektove instrukce patri do `AGENTS.md` v koreni projektu nebo v blizsim podadresari.
- Nevytvarej lokalni varianty typu `AGENTS.local.md`, pokud k tomu neni jasny duvod v projektu.
- Kdyz uzivatel pozada o upravu globalnich Codex instrukci, uprav `~/.codex/AGENTS.md` a vysvetli, co se zmenilo.

## Skills

- Sdilene skilly jsou v `~/ai-prompts-and-skills/shared-skills/`.
- Codex uzivatelske skilly maji byt dostupne pres `~/.agents/skills/`.
- Pokud je skill jen symlink, edituj zdrojovy soubor ve `shared-skills/`, ne pres symlink.
- Pri vytvoreni noveho sdileneho skillu pridej odpovidajici symlink do `~/.agents/skills/`, pokud tam jeste neni.

## MCP a externi nastroje

- Playwright MCP preferuj pred Chrome MCP pro automatizaci prohlizece.
- Telegram MCP neovladej za uzivatele. Neposilej prikazy jako `/check`, `/yes`, `/no`; Telegram ovlada uzivatel sam.
