---
name: template-client-release
description: Prenes novou verzi z template do klienta a priprav deploy. Pouzij kdyz uzivatel rika "prenest novou verzi z template do klienta", "syncni template do klienta", "priprav client release", "jak dostanu zmeny do klientske instance", "aktualizuj bezici klientskou kopii", nebo chce release workflow se zachovanim rollbacku.
allowed-tools: Bash, Read
---

# Template -> Client Release

Pouzij pro workflow, kde existuji dva oddelene checkouty:

- `template` repo = zdroj pravdy pro kod
- `client` repo = konkretni klientska instance s vlastni release historii

Typicky cil:

1. zafixovat novou verzi v `template`
2. prenest kodove zmeny do `client`
3. udelat release commit v `client`
4. pripravit bezpecny deploy a rollback

## Zasady

- Necommituj `.env`, `.env.*`, tajne klice, DB soubory, runtime data ani logy.
- Neprovadej deploy bez jasneho checkpointu.
- Commit message pouze navrhni; uzivatel musi dostat sanci ji upravit nebo nahradit.
- Rollback se sleduje v `client` repu, ne v `template`.
- Kdyz neni jasne, ktere soubory jsou klientske a ktere produktove, nejdriv se zastav a vyjasni to.

## Povinne checkpointy

Zastav se a zeptej se uzivatele pred:

1. commitem v `template`
2. syncem z `template` do `client`
3. commitem v `client`
4. samotnym deployem

Nevypisuj obecne otazky. Poloz jednu kratkou konkretni otazku s navrzenou dalsi akci.

## Postup

### 1. Ověř strukturu a git stav

Zjisti:

- kde je `template` adresar
- kde je `client` adresar
- jestli jsou oba git repozitare
- jestli ma `client` cisty worktree

Priklad:

```bash
git -C /cesta/template status --short --branch
git -C /cesta/client status --short --branch
git -C /cesta/client log --oneline -n 5
```

Pokud `client` neni cisty, zastav se. Nenasazuj pres cizi nebo neulozene zmeny.

### 2. Shrn zmeny v `template`

Vypis:

- zmenene soubory
- jestli se meni runtime kod, config, docs, testy
- jestli se podle zmen zda, ze release potrebuje nove env promene nebo datovou migraci

Priklad:

```bash
git -C /cesta/template status --short
git -C /cesta/template diff --name-only
git -C /cesta/template diff --stat
```

Pak navrhni commit message. Vezmi ji z realnych zmen, ale necommituj bez potvrzeni.

Priklad formulace:

- `Navrhuju commit message: "Add tested dashboard state persistence". Chces ji pouzit, upravit, nebo napsat vlastni?`

### 3. Commit v `template`

Po potvrzeni uzivatelem:

```bash
git -C /cesta/template add .
git -C /cesta/template commit -m "..."
git -C /cesta/template rev-parse --short HEAD
```

Zapamatuj si `template` commit hash. Ten patri do release commitu v `client`.

### 4. Priprav sync do `client`

Pred syncem vypis:

- co se bude prenaset
- co se bude vylucovat
- proc je ta hranice bezpecna

Vychozi `exclude` seznam:

- `.git/`
- `.env`
- `.env.*`
- `*.db`
- `.venv/`
- `venv/`
- `__pycache__/`
- `logs/`
- `data/`
- `tmp/`
- `.DS_Store`

Kdyz projekt obsahuje dalsi klientske artefakty, rozsir `exclude` podle kontextu.

### 5. Sync `template` -> `client`

Kdyz jsou oba checkouty na stejnem stroji a nejsou gitove svazane, preferuj `rsync`.

Priklad:

```bash
rsync -av \
  --exclude '.git/' \
  --exclude '.env' \
  --exclude '.env.*' \
  --exclude '*.db' \
  --exclude '.venv/' \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude 'logs/' \
  --exclude 'data/' \
  --exclude 'tmp/' \
  --exclude '.DS_Store' \
  /cesta/template/ \
  /cesta/client/
```

Nepouzivej `--delete` jako default. Pridej ho jen kdyz je zrejme, ze uzivatel chce plny mirror a ze v `client` nejsou samostatne soubory navic.

Pokud jsou repo gitove navazana a merge/cherry-pick dava smysl, muzes je pouzit. Kdyz si nejsi jisty, vrat se ke konzervativnimu `rsync` postupu.

### 6. Zkontroluj diff v `client`

Po syncu ukaz:

- ktere soubory se v `client` zmenily
- jestli se dotkly klientskych souboru, ktere se menit nemely

Priklad:

```bash
git -C /cesta/client status --short
git -C /cesta/client diff --stat
```

Kdyz diff vypada podezrele, zastav se a rekni proc.

### 7. Navrhni release commit v `client`

Navrhni commit message s odkazem na `template` hash.

Format doporucene message:

- `Release: sync from template <hash>`
- `Release: add <feature> from template <hash>`

Zase se zastav a nech uzivatele message potvrdit nebo prepsat.

Po potvrzeni:

```bash
git -C /cesta/client add .
git -C /cesta/client commit -m "..."
git -C /cesta/client rev-parse --short HEAD
```

### 8. Priprav rollback

Vypis:

- novy `client` release commit hash
- predchozi commit
- doporuceny rollback prikaz

Preferuj:

```bash
git -C /cesta/client revert <release_commit>
```

Nevnucuj `git reset --hard` ani prepinani commitu, pokud to uzivatel vyslovne nechce.

### 9. Priprav deploy checkpoint

Na konci shrn:

- co bylo commitnuto v `template`
- co bylo commitnuto v `client`
- jestli release vypada bezpecne pro deploy
- jestli jsou potreba env zmeny nebo migrace

Teprve pak se zeptej, jestli pokracovat deployem. Deploy samotny delej podle projektoveho nebo platformoveho skillu, napriklad `railway-deploy` nebo projektoveho deploy skillu.

## Doporuceny styl komunikace

- Bud kratky a operacni.
- Nezahlcuj uzivatele dlouhou analyzou.
- Po kazdem checkpointu rekni, co se stalo a proc je dalsi krok bezpecny.
- Commit messages navrhuj sam podle diffu, ale vzdy nech posledni slovo uzivateli.

## Minimalni zaver po release priprave

Uzivateli vrat:

- `template` commit hash
- `client` release commit hash
- jednu vetu, co se preneslo
- rollback prikaz
- dalsi krok k deployi
