---
name: odkaz-na-mobil
description: >
  Naservíruje HTML soubor nebo složku jako veřejnou https adresu přes cloudflared,
  aby to šlo hned otevřít na telefonu — i mimo domácí Wi-Fi, na mobilních datech,
  po přeposlání do iMessage nebo SMS.

  Použij kdykoliv uživatel říká:
  - "dej mi odkaz na mobil"
  - "chci to rozjet z mobilu" / "chci si to otevřít na telefonu"
  - "ať to otevřu na mobilu"
  - "pošli mi to do telefonu" / "chci si to poslat SMS nebo iMessage"
  - "budu mimo domácí síť" / "ať to funguje i na jiném účtu / jiném zařízení"
  - "/odkaz-na-mobil <cesta>"
---

# odkaz-na-mobil — z lokálního HTML klikací odkaz do telefonu

Cíl: uživatel dostane **jeden odkaz**, který na telefonu otevře to, na co se dívá
na počítači. Ne cestu k souboru, ne `file://`, ne preview panel.

---

## Režim: vždy tunel

**Výchozí a jediný běžný režim je `--tunnel`.** Důvod z praxe: odkaz skoro vždy
skončí v iMessage nebo SMS a otevírá se na mobilních datech nebo na cizí Wi-Fi —
LAN adresa `192.168.x.x` tam je mrtvá a uživatel to zjistí až v autě.
Tunel stojí navíc ~40 vteřin čekání, což je vždycky levnější než odkaz, co nejde.

LAN (bez `--tunnel`) použij jen tehdy, když uživatel **výslovně** řekne, že nic
nemá jít ven — typicky u citlivého obsahu. Pak mu ale rovnou řekni, že to bude
fungovat jen na domácí Wi-Fi.

---

## Postup

1. **Zjisti, co se má servírovat.** Jeden soubor → **zkopíruj ho do scratchpadu
   jako `index.html`** a servíruj tu složku; odkaz je pak holá adresa bez cesty,
   která se dobře posílá. Víc souborů → servíruj složku.

   > Nikdy neservíruj rovnou projektový adresář s `.md` podklady, fakturami nebo
   > osobními dokumenty — tunel je vystaví všechny. Do scratchpadu jen to, co má
   > být vidět.

2. **Zkontroluj odkazy mezi stránkami.** Absolutní `href="/dalsi.html"` funguje jen
   z kořene serveru — když servíruješ podsložku, přepiš je na relativní.
   Nikdy nepřepisuj originál: pracuj s **kopií ve scratchpadu**.

3. **Dolaď to na mobil** (do kopie, ne do originálu). Minimum, které se vyplácí:
   ```css
   @media(max-width:640px){
     .page{padding:24px 18px;border-left:none;border-right:none}
     table{display:block;overflow-x:auto}
     h1{font-size:24px}
   }
   ```
   Pevné `max-width` v px, velké postranní paddingy a široké tabulky jsou tři
   nejčastější důvody, proč stránka na telefonu leze do stran.

4. **Když je stránek víc, udělej rozcestník** `index.html` — ať stačí poslat jeden
   odkaz. Styl vezmi ze servírovaných stránek, ne z hlavy.

5. **Spusť skript** (sám si najde volný port a ověří se):
   ```bash
   nohup python3 ~/ai-prompts-and-skills/shared-skills/odkaz-na-mobil/scripts/serve_tunnel.py \
     <cesta> --tunnel > /tmp/odkaz-na-mobil.log 2>&1 &
   sleep 50; cat /tmp/odkaz-na-mobil.log
   ```
   Tunel potřebuje ~40 s: cloudflared ohlásí adresu dřív, než ji zná DNS, a skript
   proto záměrně počká, než začne ověřovat (jinak macOS zacachuje neúspěšný dotaz
   a kontrola spadne na adrese, která už za chvíli funguje).
   Běží-li z dřívějška tvůj vlastní `serve_tunnel.py` na tomtéž obsahu, nejdřív
   `pkill -f serve_tunnel.py` — jinak zbytečně přibude druhá adresa.

6. **Přečti si výstup.** Skript vypíše JSON se seznamem stránek a jejich titulky.
   Titulky musí sedět na obsah, který servíruješ. Když sedí, pošli odkaz.

7. **Zkopíruj odkaz do schránky** — ať ho uživatel nemusí označovat myší:
   ```bash
   printf '%s' "<url>" | pbcopy && echo "ve schránce: $(pbpaste)"
   ```
   (Windows: `clip`.)

---

## Jak odkaz předat (tohle je půlka skillu)

**Vždy vypiš odkaz v chatu jako samostatný `code block`**, ne jako markdown odkaz
schovaný pod textem. Uživatel ho kopíruje a vkládá do iMessage — potřebuje holý
text, na jeden klik, bez závorek a bez okolních slov:

````
```
https://nazev-tunelu.trycloudflare.com
```
````

K tomu přidej **cestu do iMessage** (jednou, stručně, ne přednáška):

1. Otevřít **Zprávy** na Macu (Command mezerník → „Zprávy“).
2. Do pole *Komu* napsat **vlastní číslo nebo Apple ID** — sobě iMessage poslat lze,
   objeví se to na telefonu.
3. Text vložit přes **Command V** a odeslat.

A doplň dvě věci, které ušetří další kolo:

- Na iPhonu si stránku dát **Sdílet → Přidat na plochu**, ať se nehledá v historii.
- Kdo má zapnutý **Universal Clipboard** (stejné Apple ID, Bluetooth i Wi-Fi na obou
  zařízeních), nemusí přes Zprávy vůbec — odkaz je už ve schránce a na iPhonu se
  vloží dlouhým stiskem → Vložit.

---

## Tvrdá pravidla (nikdy se neptej, prostě dodrž)

1. **Nikdy nepředpokládej, že port je volný, a nikdy nekilluj cizí proces.**
   Souběžně běží víc serverů z jiných projektů. Skript port přeskočí a vezme další.
   Killuj jen `serve_tunnel.py` a `cloudflared`, které jsi sám spustil.
2. **Vždy ověř podle titulku, že na portu odpovídá tvůj obsah.** Když se bind
   nepovede, na portu klidně odpovídá cizí server a odkaz tiše vede na cizí projekt.
   `HTTP 200` sám o sobě nedokazuje vůbec nic. (Tohle je nejdražší chyba tady.)
3. **Porty 8080–8089 jsou rezervované pro mail-agent** — skript proto začíná na 9200.
4. **Nikdy needituj zdrojové HTML.** Mobilní CSS a přepis odkazů jde do kopie.
5. **Nikdy neposílej `file://` ani cestu k souboru.** Jen http(s) odkaz.
6. **Odkaz vždy ověř před odesláním** — ne curl na `/`, ale titulek každé stránky.
7. **Odkaz vždy v code blocku a zároveň ve schránce.** Markdown odkaz v textu se
   z mobilního chatu kopíruje blbě.

---

## Když upravuješ skript

Systémový python na Macu je **3.9** (z Xcode) — žádné `str | None` v anotacích,
jinak skript spadne hned při importu. Po každé úpravě ho spusť naostro
a přečti si výstup; syntaktická kontrola sama nestačí.

## Cloudflared

macOS: `brew install cloudflared` · Windows: `winget install Cloudflare.cloudflared`

Quick tunnel (`--url`) nepotřebuje účet ani doménu. Adresa je náhodná a při každém
spuštění jiná.

---

## Co říct uživateli (obojí, jednou větou, ne přednáška)

- **Platnost:** odkaz žije, jen dokud běží počítač a proces. Po uspání je mrtvý
  a příště bude adresa jiná.
- **Expozice:** adresa je veřejná — kdo ji zná, obsah vidí, bez hesla.
  Řekni to zvlášť, když stránka obsahuje ceny, kontakty, podklady k jednání
  nebo cokoli osobního, a pojmenuj konkrétně, co na té stránce je.

Trvalá alternativa, když má odkaz vydržet: publikovat stránku jako artifact
a sdílení zapnout na stránce v jejím menu.

---

## Vypnutí

```bash
pkill -f serve_tunnel.py; pkill -f "cloudflared tunnel"
```
Killuj jen procesy, které jsi sám spustil.
