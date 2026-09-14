#!/usr/bin/env bash
# serve.sh — naservíruje složku přes http.server na STABILNÍM portu.
#
# Proč: skilly, které dělají localhost náhled (prezentace, report…), dřív
# spouštěly `python3 -m http.server <volný port>` při každém běhu a starý
# server nikdo nezabil. Po pár regeneracích tak běželo 6+ statických serverů
# téže složky, každý na jiném portu (5191, 8104, 8107, 8200…). Tenhle skript
# to řeší: jedna složka = jeden port. Když už server pro tuhle složku běží,
# jen ho znovupoužije, takže regeneruješ pořád tutéž verzi na téže adrese.
#
# Použití:  serve.sh [SLOZKA] [SOUBOR]
#   SLOZKA — složka k servírování (default: aktuální adresář)
#   SOUBOR — soubor, na který má vést odkaz (default: "/")
# Na stdout vypíše hotovou URL.
#
# macOS/Linux (lsof, pgrep, python3). Na Windows se localhost náhled nedělá.

set -euo pipefail

DIR="$(cd "${1:-.}" && pwd)"
FILE="${2:-}"

# Cesty normalizujeme přes Python: lsof -Fn escapuje non-ASCII byty jako
# doslovný text "\xc5\xaf" a navíc se na macOS liší unicode normalizace
# (lsof NFD × shellové `pwd` NFC). Bez toho by se "Můj disk" nikdy neshodlo
# a reuse by nefungoval. Funkce dekóduje \xNN zpět na byty a vrátí NFC —
# funguje jak na cestě z lsof (escapovaná), tak na čisté cestě z `pwd`.
_path() {
  python3 -c '
import sys, unicodedata as u
raw = sys.argv[1]; out = bytearray(); i = 0
while i < len(raw):
    if raw[i] == "\\" and raw[i+1:i+2] == "x":
        out.append(int(raw[i+2:i+4], 16)); i += 4
    else:
        out += raw[i].encode("utf-8"); i += 1
print(u.normalize("NFC", out.decode("utf-8", "surrogateescape")))
' "$1"
}
DIR_NFC="$(_path "$DIR")"

# Deterministický port z cesty: stejná složka → vždy stejný port
# (8090–8489, mimo rezervované 8080–8089 pro mail-agent).
hash=$(printf '%s' "$DIR_NFC" | cksum | cut -d' ' -f1)
PORT=$(( 8090 + hash % 400 ))

# Běží už MŮJ http.server přesně pro tuhle složku (na jakémkoli portu)?
# Když ano, znovupoužij jeho port — neplodíme nový proces.
existing_port=""
for pid in $(pgrep -f 'http\.server' 2>/dev/null || true); do
  cwd=$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
  [ -z "$cwd" ] && continue
  [ "$(_path "$cwd")" = "$DIR_NFC" ] || continue
  existing_port=$(lsof -nP -a -p "$pid" -iTCP -sTCP:LISTEN 2>/dev/null \
    | grep -oE ':[0-9]+ \(LISTEN\)' | grep -oE '[0-9]+' | head -1)
  [ -n "$existing_port" ] && break
done

if [ -n "$existing_port" ]; then
  PORT="$existing_port"
else
  # Deterministický port drží někdo cizí (jiná složka)? Posuň se výš —
  # cizí procesy nekillujeme.
  while lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do
    PORT=$(( PORT + 1 ))
  done
  ( cd "$DIR" && nohup python3 -m http.server "$PORT" --bind 127.0.0.1 \
      >/dev/null 2>&1 & )
  sleep 0.5
fi

echo "http://127.0.0.1:${PORT}/${FILE}"
