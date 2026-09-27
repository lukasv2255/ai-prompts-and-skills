---
name: uklid-mac
description: >
  Diagnostika macOS: co žere místo na disku, co žere paměť a proč je počítač pomalý.
  Read-only sken, který každý nález zařadí do jedné ze tří kategorií — **mrtvé smetí**
  (zmizí navždy, nic se nedoinstaluje), **znovustažitelné artefakty** (smazání je jen
  půjčka, příště se to stáhne zpátky) a **data** (nikdy). Navrhuje jen první kategorii;
  druhou vypíše s cenou za opětovné stažení a čeká na výslovný pokyn. Mazání provádí
  po jednotlivých položkách, až po odsouhlasení.

  Použij kdykoliv uživatel říká:
  - "ukliď mac" / "ukliď počítač" / "udělej pořádek na disku"
  - "dochází mi místo" / "co mi žere místo na disku"
  - "počítač je pomalý" / "zrychli mi to" / "proč to seká"
  - "co mi běží na pozadí" / "co mi žere paměť"
  - "ukliď tapety" / "promaž tapety" / "/uklid-mac tapety"
  - "/uklid-mac"
---

# Úklid a zrychlení Macu

## Vůdčí princip: nemazat nic, co se bude muset doinstalovat

Klasický "cleaner" ušetří 10 GB tím, že smaže cache balíčkovačů a stažené browsery.
Za týden je to zpátky, akorát to mezitím stálo čas a data. **To není úspora, to je půjčka.**

Proto každý nález dostane kategorii a **návrh se dělá jen z kategorie A**:

| | Kategorie | Co to znamená | Co s tím |
|---|---|---|---|
| 🟢 | **A — mrtvé** | Zmizí a nikdy se nevrátí. Nic se nedoinstaluje, žádný nástroj to nebude postrádat. | Navrhni ke smazání. |
| 🟡 | **B — znovustažitelné** | Smazání funguje, ale při dalším použití se to stáhne zpátky. | **Nenavrhuj.** Vypiš zvlášť s odhadem "cena: X GB re-download". Smaž jen na výslovný pokyn. |
| 🔴 | **C — data** | Nenahraditelné nebo uživatelovo. | Nikdy nemazat. Jen ukázat velikost. |

Rozhodovací test pro zařazení — **„co se stane, až to bude příště potřeba?"**

- *Nic, ta věc už neexistuje / je nainstalovaná / je po expiraci* → **A**
- *Stáhne se to znovu* → **B**
- *Je to pryč* → **C**

Když si u položky nejsi jistý, patří do B. Nikdy nehádej ve prospěch mazání.

## Druhá polovina: zrychlení není mazání

Většina „pomalého Macu" nemá příčinu v plném disku, ale v **paměti a procesech**.
Sken proto vždy měří obojí a odděluje to v reportu. Typické skutečné příčiny:

- **Swap** — když `vm.swapusage` ukazuje jednotky GB *used*, systém odkládá paměť na disk.
  To je nejsilnější signál zpomalení. Hledej, kdo RAM drží.
- **Prohlížeč** — bývá největší jednotlivý žrout, běžně víc než všechno ostatní dohromady.
- **Agenti na pozadí** — dashboardy, boti, collectory. Nebolí jeden, bolí dvacet.
- **Selhávající launchd joby** — nenulový exit v `launchctl list` znamená, že se to
  v cyklu restartuje. Žere CPU a dělá to potichu.
- **Volné místo pod ~10 %** — APFS nemá kam zapisovat, swap se nemá kam odkládat.
- **Dlouhý uptime** — swap se nevyčistí sám; po týdnech je restart legitimní řešení.

## Postup

### 1. Sken

Spusť `scripts/diagnostika.sh` z adresáře skillu. Je **read-only** — nic nemaže,
nic nevypíná, nepotřebuje sudo. Trvá do minuty.

```
bash "$(dirname SKILL.md)/scripts/diagnostika.sh"
```

Výstup má sekce `## DISK`, `## PAMET`, `## PROCESY`, `## LAUNCHD`, `## SIROTCI`.
Čti ho jako podklad, ne jako hotový report.

### 2. Zařazení nálezů

Projdi výstup proti katalogu v `reference/kategorie.md`. Ten drží zařazení pro běžné
cesty. Co v katalogu není, zařaď podle testu výše — a **přidej to do katalogu**,
ať to příště nemusíš řešit znovu.

Zvláštní pozornost dvěma věcem, které skript hlásí zvlášť:

- **Sirotci po odinstalovaných aplikacích** — launchd plisty, updatery, audio drivery
  a podpůrné složky aplikací, které na disku už nejsou. Skript ověřuje existenci
  mateřské aplikace, takže tohle je spolehlivá kategorie A.
- **Jednotlivé nafouklé logy** — log přes ~100 MB nemá být smazán, ale **rotován**.
  Navrhni rotaci (`newsyslog`, `logrotate`, nebo limit přímo v aplikaci), ne `rm`.
  Smazat log bez opravy příčiny znamená, že za měsíc je zpátky.

### 3. Report

Uživateli vypiš tabulku v tomhle pořadí a nic nemaž:

1. **Volné místo teď** a kolik by šlo získat z kategorie A.
2. **🟢 Návrh ke smazání** — položka, velikost, jednou větou proč se nevrátí.
3. **🟡 Znovustažitelné** — jen na vědomí, s cenou za re-download. Výslovně napiš,
   že to nenavrhuješ.
4. **🔴 Velká data** — co zabírá místo, ale je uživatelovo.
5. **Zrychlení** — oddělená sekce. Swap, největší žrouti RAM, selhávající joby,
   agenti, kteří běží zbytečně.

Buď stručný. U každé položky jedna věta, ne odstavec.

### 4. Mazání

Až na výslovný pokyn. Pak:

- Maž **po skupinách, které uživatel jmenoval** — ne „všechno z návrhu".
- Před každým `rm -rf` ověř, že cesta existuje a sedí velikost.
- Co patří rootu, nemaž přes `sudo` na slepo — vypiš uživateli příkaz, nebo použij
  přesun do koše přes Finder (`osascript -e 'tell application "Finder" to delete POSIX file "..."'`),
  kde macOS sám vyžádá autorizaci.
- **Koš nikdy nevysypávej.** To je nevratné smazání a patří uživateli.
- Po dokončení ověř `df -h /` a řekni skutečně uvolněné místo, ne odhad.

## Podpříkaz `tapety`

Na „ukliď tapety" / „promaž tapety" / `/uklid-mac tapety` spusť `scripts/tapety.sh`.
Smaže stažená aerial videa z `~/Library/Application Support/com.apple.wallpaper/aerials/videos/`.

Proč to má vlastní přepínač: macOS si dotahuje dynamické tapety z knihovny o 156
kusech po jednom (0,14–0,96 GB za kus) a **sám je nikdy nemaže**. Za pár týdnů to
jsou jednotky GB. Střídání tapet a dotahování knihovny je přitom v macOS jedna
a tatáž funkce — oddělit je nejde, takže kdo chce rotaci, musí počítat s růstem.

Tohle je proto vědomá výjimka z pravidla „nemazat znovustažitelné": uživatel ví,
že se videa stáhnou znovu, a volí periodické promazávání místo vypnuté rotace.
Skript nesahá na nastavení tapet a nic nevypíná.

`--dry-run` vypíše, co by smazal, včetně názvů videí z manifestu.

## Co tenhle skill nedělá

- Nevypíná ani neodinstalovává uživatelovy agenty a dashboardy. Navrhne, které vypadají
  nepoužívaně, a rozhodnutí nechá na uživateli.
- Nesahá na `/System`, SIP-chráněné cesty ani na `sudo` operace bez odsouhlasení.
- Nevysypává koš, nemaže Downloads plošně, nemaže nic z `~/Documents`, `~/Desktop`
  a z cloudových mountů (Google Drive, iCloud, Dropbox) — tam smazání propíše změnu
  na ostatní zařízení a je fakticky nevratné.
- Neinstaluje žádný cleaner třetí strany.
