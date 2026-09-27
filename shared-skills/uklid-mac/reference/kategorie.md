# Katalog: co je mrtvé, co se vrátí, a čeho se nedotýkat

Zařazení podle jediného testu: **co se stane, až to bude příště potřeba?**
Nic → A. Stáhne se to znovu → B. Je to pryč → C.

Když cesta v katalogu není, zařaď ji podle testu a **doplň ji sem**.

---

## 🟢 A — mrtvé (navrhuj ke smazání)

Nic z toho se nedoinstaluje. Buď to patří k aplikaci, která už neexistuje, nebo to
splnilo účel a leží tam navždy.

| Cesta / typ | Proč je to mrtvé |
|---|---|
| `~/Library/Caches/*.ShipIt` | Stažené **staré** instalátory updatů (VS Code, Claude, Electron appky). Update už proběhl, balík se nikdy nepoužije. |
| `~/Library/Containers/<bundle-id>` bez nainstalované aplikace | Sandbox složka po odinstalované appce. Nemá ji kdo otevřít. |
| `~/Library/Group Containers/*` bez mateřské aplikace | Totéž. |
| `~/Library/Application Support/<appka>` po odinstalaci | Totéž. |
| launchd plist ukazující na neexistující binárku | Mrtvý job, launchd ho jen marně zkouší. |
| Updater bez produktu (Microsoft AutoUpdate, Google Keystone) | Hlídá updaty něčeho, co tu není. |
| `/Library/Audio/Plug-Ins/HAL/*.driver` odinstalované appky | Zůstává po Teams / Zoom. Zabírá málo, ale sedí v audio řetězci. |
| Instalátory (`*.dmg`, `*.pkg`) už nainstalovaného software | Aplikace běží, instalátor je hotová věc. |
| `~/Library/Application Support/MobileSync/Backup/*` staré zálohy iPhonu | Zálohy zařízení, která už nemáš / dávno přepsané iCloudem. **Ověř datum a zařízení, než navrhneš.** |
| `/private/var/db/diagnostics` nad ~1 GB | Systémové diagnostické logy. Rotují se samy, ale pomalu. Systém si je nevyžádá zpět. |
| `~/Library/Developer/Xcode/iOS DeviceSupport/<stará verze>` | Symboly pro verze iOS, které už na žádném tvém zařízení neběží. |
| Osamocené `.crash` / `.diag` reporty starší než rok | Nikdo je nikdy neotevře. |

---

## 🟡 B — znovustažitelné (NENAVRHUJ, jen vypiš s cenou)

Smazání funguje a místo se uvolní. Jenže při dalším `pip install`, `npm ci`, buildu
nebo spuštění nástroje se to stáhne zpátky — stojí to čas, data a někdy i verzi,
která už na indexu není.

**Pravidlo: tohle se maže jen tehdy, když uživatel výslovně řekne „ano, i to, co se stáhne znovu".**

| Cesta | Co se stane po smazání | Orientační cena |
|---|---|---|
| `~/Library/Caches/ms-playwright` | Playwright si při dalším běhu stáhne browsery. | ~1 GB, minuty |
| `~/Library/Caches/pip`, `~/.cache/uv` | Každý další `pip install` tahá z PyPI místo z disku. | stovky MB |
| `~/.npm`, `~/Library/pnpm/store` | `npm ci` / `pnpm install` jede z registry. pnpm store navíc **sdílí balíčky mezi projekty** — smazáním se nafouknou všechna `node_modules`. | stovky MB |
| `~/.cargo/registry`, `~/go/pkg/mod` | Další build stahuje závislosti znovu. | stovky MB až GB |
| `~/Library/Caches/Homebrew` | Stažené lahve. `brew cleanup --prune=all` je bezpečnější — smaže jen **staré verze**, ne aktuální. *(Samotný `brew cleanup` je vlastně A, protože staré verze se nevrátí.)* |
| `~/.ollama/models` | Model se stahuje znovu, a to jsou jednotky až desítky GB. | velmi drahé |
| Docker / OrbStack images | Další `docker run` tahá image z registry. | GB |
| `node_modules` v projektech | `npm install` to vrátí — ale rozbije to rozjetý projekt do doby, než ho pustíš. | podle projektu |
| `.venv` v projektech | Totéž, plus riziko jiných verzí balíčků než původně. | podle projektu |
| `~/Library/Developer/Xcode/DerivedData` | Další build je od nuly, tedy dlouhý. Občas ale léčí podivné build chyby. | podle projektu |
| `~/Library/Application Support/com.apple.wallpaper/aerials` | macOS si videa stáhne, až tapetu nebo spořič použiješ. | GB |
| Cache prohlížeče | Weby se načtou pomaleji, dokud se cache nenaplní. | stovky MB |
| Chrome profily pro automatizaci (CDP, scrapery) | **Smazáním zmizí i přihlášení.** Scraper pak potřebuje nový login. Správné řešení je smazat uvnitř profilu jen `Default/Cache` a `Default/Code Cache`, ne celý profil. | viz poznámka níže |

---

## 🔴 C — data (nikdy nemazat)

| Co | Poznámka |
|---|---|
| `~/Documents`, `~/Desktop`, `~/Pictures`, `~/Movies` | Uživatelovo. Nanejvýš ukázat velikost. |
| Cokoliv v cloudovém mountu — Google Drive, iCloud Drive, Dropbox | Smazání se **propíše na všechna ostatní zařízení**. Fakticky nevratné. |
| Disky virtuálů (`*.utm`, `*.vmwarevm`, `*.qcow2`) | Celý nainstalovaný systém i s daty. Bývá největší položka na disku a přesto se nemaže. |
| Git repozitáře, projekty, `*.db`, SQLite | Práce. |
| Koš | Vysypání je nevratné mazání — dělá ho uživatel. |
| Fotky, media knihovny, zálohy klíčů, `~/.ssh`, `~/.gnupg` | Samozřejmost. |
| `.env`, konfigurace s tokeny | Ani jako „cache" nevypadající soubory. |

---

## Zvláštní případy

### Nafouklý log
Log nad ~100 MB **nemaž — zaveď rotaci.** Smazání bez opravy příčiny znamená,
že za měsíc je zpátky ve stejné velikosti. Možnosti podle toho, kdo log píše:

- Python: `logging.handlers.RotatingFileHandler(maxBytes=..., backupCount=3)`
- launchd job přesměrovaný do souboru: rotace přes `newsyslog.conf`
- rychlá úleva bez restartu procesu: `: > soubor.log` (zkrátí soubor, ale
  drží deskriptor — proces píše dál a nespadne)

### Chrome profily pro automatizaci
Scraperům rostou profily donekonečna, protože jim nikdo nečistí cache. Smazat
celý profil znamená přijít o přihlášení. Čisti jen cache uvnitř:

```
<profil>/Default/Cache
<profil>/Default/Code Cache
<profil>/Default/Service Worker/CacheStorage
<profil>/Default/GPUCache
```

Cookies, `Login Data` a `Local Storage` nech být — tam je session.
Dělej to při zavřeném prohlížeči.

### Swap a restart
Swap se sám nevyčistí. Po týdnech uptime je restart legitimní a nejúčinnější
„zrychlení" — ne proto, že by macOS něco „ucpával", ale protože se tím zahodí
odložené stránky a fragmentovaná paměť dlouho běžících procesů.

### Selhávající launchd job
Nenulový `exit` v `launchctl list` znamená opakovaný restart v cyklu. Řeš příčinu,
neodstraňuj job automaticky — může to být něco, co uživatel potřebuje.
Exit `78` bývá chyba konfigurace, `1` obecná chyba, záporná čísla jsou signály
(`-9` SIGKILL = často došla paměť, `-15` SIGTERM = někdo ho ukončil).
