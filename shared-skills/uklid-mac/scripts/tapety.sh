#!/bin/bash
# uklid-mac tapety — smaže stažená aerial videa (dynamické tapety a spořiče).
#
# macOS je postupně dotahuje z knihovny o 156 kusech a sám je nemaže, takže
# rostou donekonečna. Střídání tapet zůstává zapnuté: co bude potřeba, stáhne
# se znovu. Tohle je vědomá volba "radši občas promažu, než abych přišel
# o rotaci" — proto skript nic nevypíná a na nastavení nesahá.
#
#   tapety.sh            smaže stažená videa
#   tapety.sh --dry-run  jen ukáže, co by smazal

set -u
export LC_ALL=C
[ "$(uname -s)" = "Darwin" ] || { echo "Jen pro macOS."; exit 1; }

DRY=0
[ "${1:-}" = "--dry-run" ] && DRY=1

A="$HOME/Library/Application Support/com.apple.wallpaper/aerials"
V="$A/videos"

[ -d "$V" ] || { echo "Složka s tapetami neexistuje — není co mazat."; exit 0; }

count=$(find "$V" -maxdepth 1 -name '*.mov' | wc -l | tr -d ' ')
[ "$count" -gt 0 ] || { echo "Žádná stažená videa — není co mazat."; exit 0; }

size=$(du -shx "$V" 2>/dev/null | cut -f1)
free_before=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}')

# Názvy z manifestu, ať je vidět, co konkrétně mizí
python3 - "$A" <<'PY' 2>/dev/null || find "$V" -maxdepth 1 -name '*.mov' -exec basename {} \; | sed 's/^/  /'
import json, os, subprocess, sys, glob, plistlib
base = sys.argv[1]
try:
    d = json.load(open(base + '/manifest/entries.json'))
    assets = d.get('assets', d)
    loc = base + '/manifest/TVIdleScreenStrings.bundle/Contents/Resources/en.lproj/Localizable.nocache.strings'
    names = {}
    try:
        names = plistlib.loads(subprocess.run(
            ['plutil', '-convert', 'xml1', '-o', '-', loc],
            capture_output=True).stdout)
    except Exception:
        pass
    have = {os.path.basename(f)[:-4]: f for f in glob.glob(base + '/videos/*.mov')}
    rows = []
    for a in assets:
        if a['id'] in have:
            n = names.get(a.get('localizedNameKey', ''), a.get('accessibilityLabel', a['id']))
            rows.append((os.path.getsize(have[a['id']]) / 2**30, n))
    for s, n in sorted(rows, reverse=True):
        print(f'  {s:5.2f} GB  {n}')
except Exception:
    raise SystemExit(1)
PY

printf '\n%s videí, %s celkem\n' "$count" "$size"

if [ "$DRY" = "1" ]; then
  echo "(--dry-run: nic nesmazáno)"
  exit 0
fi

find "$V" -maxdepth 1 -name '*.mov' -delete
# Náhledy jsou malé, ale bez videí nemají smysl a stáhnou se s nimi.
rm -rf "$A/thumbnails" 2>/dev/null

free_after=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}')
printf 'Smazáno. Volno: %s GB → %s GB (+%s GB)\n' \
  "$free_before" "$free_after" "$((free_after - free_before))"
echo "Střídání tapet zůstává zapnuté — macOS si další videa postupně stáhne."
