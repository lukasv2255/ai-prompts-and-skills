---
name: launchd-agent
description: Sprava dlouhodobe beziciho procesu pres launchd na macOS. Pouzij kdyz uzivatel rika "restartuj agenta", "spust sluzbu na Macu", "launchd", "plist", "background proces na macOS", nebo kdyz je potreba udelat stabilni auto-start a auto-restart bez tray aplikace.
---

# Launchd Agent

Obecny skill pro dlouhodobe bezici Python procesy na macOS pres `launchd`.

Preferuj ho pro agenty, collectory a boty, kteri maji bezet stabilne na pozadi.
Pokud ma projekt vlastni launchd skill, pouzij nejdriv ten projektovy.

## Kdy ho pouzit

- spusteni procesu po prihlaseni uzivatele
- automaticky restart po padu
- sprava `plist` souboru
- kontrola, jestli sluzba skutecne bezi
- odstraneni rucniho `nohup` workflow

## Zakladni pravidla

- `launchd` je standardni volba pro dlouhodoby background beh na macOS.
- Nepouzivej ho pro jednorazove testy nebo kratke validace.
- Po zmene `plist` proved unload nebo bootout a potom znovu load/bootstrap.
- Overuj realny stav: `launchctl list`, PID, logy a jestli proces bezi ze spravne cesty.
- Kdyz je potreba GUI ovladani pres menu bar, to uz je special-case pro tray workflow.

## Obecny postup

### 1. Najdi nebo vytvor `plist`

Projekt by mel mit `plist` nebo `*.template`, ktery:

- spousti spravny Python a skript
- ma absolutni cesty
- loguje stdout a stderr
- ma zvolenou restart policy

Pokud projekt generuje `plist` skriptem, preferuj ten generator pred rucni editaci.

### 2. Instalace do `~/Library/LaunchAgents/`

Typicky:

```bash
cp /cesta/k/sluzbe.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/sluzba.plist
```

Nebo projektovym instalacnim skriptem, pokud existuje.

### 3. Start, stop, restart

Zakladni tvary:

```bash
launchctl start <label>
launchctl stop <label>
launchctl kickstart -k gui/$(id -u)/<label>
launchctl list | grep <cast-labelu>
```

Konkretni `label` ber z projektu nebo z `plist`.

### 4. Po zmene `plist`

Pouzij plny reload:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/sluzba.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/sluzba.plist
```

Pokud projekt pouziva starsi `load/unload` workflow, respektuj jeho dokumentaci.

### 5. Overeni po spusteni

Zkontroluj:

- `launchctl list`
- jestli existuje bezici PID
- logy stdout a stderr
- ze proces bezi ze spravneho projektu

Na macOS podle potreby:

```bash
ps aux | grep <nazev_skriptu>
lsof -p <pid> | grep cwd
tail -f /cesta/k/logu
```

## Restart policy

Rozhoduj mezi:

- `KeepAlive: true` — vzdy restartovat
- `KeepAlive: false` — nikdy automaticky nerestartovat
- `KeepAlive: { SuccessfulExit: false }` — restartovat jen pri padu

Treti varianta je casto nejrozumnejsi produkcni default.

## Rizika

- Rucni spusteni stejneho procesu vedle `launchd` muze vytvorit druhou instanci.
- Relativni cesty v `plist` casto povedou ke spatnemu `cwd`.
- Dvojite logovani v kodu i v `launchd` muze duplikovat radky v logu.

## Co vratit uzivateli

- jaky `label` sluzba pouziva
- kde je `plist`
- jak se sluzba restartuje
- kde jsou logy
- jestli je workflow v poradku nebo co je rozbite
