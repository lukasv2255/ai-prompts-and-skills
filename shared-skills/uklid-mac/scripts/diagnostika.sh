#!/bin/bash
# uklid-mac — read-only diagnostika macOS.
# Nic nemaže, nic nevypíná, nepotřebuje sudo. Výstup je podklad pro report,
# zařazení do kategorií A/B/C dělá agent podle reference/kategorie.md.

set -u
export LC_ALL=C

[ "$(uname -s)" = "Darwin" ] || { echo "Tenhle skill je jen pro macOS."; exit 1; }

# Velikosti počítáme jen na bootovacím svazku (-x / -xdev). Cloudové mounty
# (Google Drive, iCloud, Dropbox) se tím vynechají schválně: jejich obsah se
# nemaže a `du` by přes ně zbytečně stahoval streamované soubory.

# `timeout` na macOS ve výchozím stavu není (je v coreutils). Fallback musí být
# definovaný dřív, než ho použije kterákoliv funkce níž.
if command -v gtimeout >/dev/null 2>&1; then
  timeout() { gtimeout "$@"; }
elif ! command -v timeout >/dev/null 2>&1; then
  timeout() { shift; "$@"; }
fi

# Cloudové mounty se do skenu nepočítají: jejich obsah se nikdy nemaže a `du`
# by přes ně stahoval streamovaný obsah.
CLOUD_SKIP=( -not -path '*/Mobile Documents/*' -not -path '*/Google Drive*/*'
             -not -path '*/Můj disk/*' -not -path '*/My Drive/*'
             -not -path '*/Dropbox/*' -not -path '*/OneDrive*/*'
             -not -path '*/Library/CloudStorage/*' )

h() { printf '\n## %s\n' "$1"; }
sub() { printf '\n--- %s\n' "$1"; }
# du, které nespadne na chybějící cestě a nikdy neběží věčně
sz() { [ -e "$1" ] && timeout 60 du -shx "$1" 2>/dev/null | cut -f1 || true; }
row() { s=$(sz "$1"); [ -n "${s:-}" ] && printf '  %-8s %s\n' "$s" "$1"; }
# velikost jednoho souboru — stat je proti du okamžitý
fsz() { awk -v b="$(stat -f '%z' "$1" 2>/dev/null || echo 0)" \
  'BEGIN{u="B";s=b; if(s>1073741824){s/=1073741824;u="G"}else if(s>1048576){s/=1048576;u="M"}
   printf "%.0f%s", s, u}'; }

printf '# DIAGNOSTIKA MACU  —  %s\n' "$(date '+%d-%m-%Y %H:%M CET')"
printf '%s, macOS %s, uptime%s\n' \
  "$(sysctl -n hw.model 2>/dev/null)" \
  "$(sw_vers -productVersion 2>/dev/null)" \
  "$(uptime | sed 's/.*up//;s/,[^,]*load.*//')"

# ---------------------------------------------------------------- DISK
h "DISK"
df -h / /System/Volumes/Data 2>/dev/null | awk 'NR==1||/Data|disk.s1s1/'

free_gb=$(df -g /System/Volumes/Data 2>/dev/null | awk 'NR==2{print $4}')
cap=$(df -h /System/Volumes/Data 2>/dev/null | awk 'NR==2{print $5}')
printf '\nVolno: %s GB  (zaplněno %s)\n' "${free_gb:-?}" "${cap:-?}"
case "${cap%\%}" in
  9[0-9]|100) echo "POZOR: pod 10 % volna — APFS i swap mají málo prostoru, tohle samo o sobě zpomaluje systém." ;;
esac

sub "Domovské složky"
for d in ~/Downloads ~/Documents ~/Desktop ~/Movies ~/Pictures ~/Music; do row "$d"; done

sub "~/Library — největší"
timeout 120 du -shx ~/Library/* 2>/dev/null | sort -rh | head -8

sub "Caches — největší"
timeout 120 du -shx ~/Library/Caches/* 2>/dev/null | sort -rh | head -12

sub "Application Support — největší"
timeout 120 du -shx ~/Library/Application\ Support/* 2>/dev/null | sort -rh | head -10

sub "Containers — největší"
timeout 120 du -shx ~/Library/Containers/* 2>/dev/null | sort -rh | head -8

sub "Vývojové cache (pozor: skoro vše kategorie B — stáhne se znovu)"
for d in ~/Library/Caches/pip ~/.npm ~/Library/pnpm ~/.cache/uv ~/.cargo/registry \
         ~/Library/Caches/deno ~/Library/Caches/ms-playwright ~/Library/Caches/Homebrew \
         ~/.ollama ~/Library/Containers/com.docker.docker ~/.orbstack; do row "$d"; done

sub "Vývojové artefakty (kategorie B — znovu se vygenerují buildem)"
for d in ~/Library/Developer/Xcode/DerivedData ~/Library/Developer/CoreSimulator \
         ~/Library/Developer/Xcode/iOS\ DeviceSupport; do row "$d"; done

sub "Zálohy a snapshoty"
row ~/Library/Application\ Support/MobileSync/Backup
snaps=$(tmutil listlocalsnapshots / 2>/dev/null | grep -c 'com.apple')
echo "  APFS lokální snapshoty Time Machine: ${snaps:-0}"
[ "${snaps:-0}" -gt 0 ] && echo "  (drží místo, které df hlásí jako volné; mizí samy, nebo 'tmutil deletelocalsnapshots <datum>')"

sub "Systémové logy a diagnostika"
for d in /private/var/log /private/var/db/diagnostics /Library/Logs ~/Library/Logs; do row "$d"; done

sub "Jednotlivé velké soubory na lokálním disku (>200 MB)"
find ~ -xdev -type f -size +200M \
     -not -path '*/Library/Caches/*' -not -path '*/.Trash/*' \
     -not -path '*/Library/Containers/*' "${CLOUD_SKIP[@]}" 2>/dev/null \
  | while read -r f; do printf '  %-8s %s\n' "$(fsz "$f")" "$f"; done | sort -rh | head -15
echo "  (cloudové mounty — Google Drive, iCloud, Dropbox — jsou ze skenu vynechané schválně)"

sub "Nafouklé logy (>100 MB — patří rotace, ne rm)"
find ~ -xdev -type f \( -name '*.log' -o -name '*.log.*' \) -size +100M \
     "${CLOUD_SKIP[@]}" 2>/dev/null \
  | while read -r f; do printf '  %-8s %s\n' "$(fsz "$f")" "$f"; done | sort -rh | head -10

sub "Koš"
row ~/.Trash
echo "  (vysypání je nevratné mazání — dělá ho uživatel, ne agent)"

# ---------------------------------------------------------------- PAMET
h "PAMET"
sysctl -n hw.memsize 2>/dev/null | awk '{printf "RAM: %.0f GB\n", $1/1073741824}'
sysctl vm.swapusage 2>/dev/null | sed 's/vm.swapusage: /Swap: /'
sysctl vm.swapusage 2>/dev/null | grep -qE 'used = ([1-9][0-9]*\.[0-9]+M|[0-9.]+G)' && {
  used=$(sysctl -n vm.swapusage | sed -n 's/.*used = \([0-9.]*\)M.*/\1/p')
  [ -n "${used:-}" ] && [ "${used%%.*}" -gt 2000 ] 2>/dev/null && \
    echo "POZOR: swap přes 2 GB — systém odkládá paměť na disk. Tohle je nejčastější příčina 'pomalého Macu'."
}
memory_pressure 2>/dev/null | tail -2

sub "RAM po skupinách"
ps -Aceo rss,comm 2>/dev/null | awk '
  NR>1 { r=$1; c=$0; sub(/^ *[0-9]+ +/,"",c); t+=r
    if (c ~ /^Google Chrome|^Chrome|^Safari|^firefox|^Arc|^Brave/) b+=r
    else if (c ~ /^Claude|^claude|^Electron|^Slack|^Discord|^Notion/) e+=r
    else if (c ~ /[Pp]ython/) p+=r
    else if (c ~ /^Code|^node|^bun|^deno/) n+=r
    else if (c ~ /[Jj]ava/) j+=r
    else if (c ~ /docker|qemu|UTM|Virtual/) v+=r
    else o+=r }
  END { f="  %-22s %7.0f MB\n"
    if(b)printf f,"prohlížeč:",b/1024;    if(e)printf f,"desktop appky:",e/1024
    if(p)printf f,"Python (agenti):",p/1024; if(n)printf f,"editor / node:",n/1024
    if(j)printf f,"Java:",j/1024;          if(v)printf f,"virtualizace:",v/1024
    if(o)printf f,"zbytek:",o/1024;        printf f,"CELKEM:",t/1024 }'

sub "Top 10 spotřebitelů RAM"
ps -Aceo pid,rss,comm -m 2>/dev/null | awk 'NR>1&&NR<=11{printf "  %-7s %7.0f MB  %s\n",$1,$2/1024,substr($0,index($0,$3))}'

# ---------------------------------------------------------------- PROCESY
h "PROCESY"
uptime | sed 's/^/Load: /'
sub "Top 10 CPU"
ps -Aceo pid,pcpu,comm -r 2>/dev/null | awk 'NR>1&&NR<=11{printf "  %-7s %5s%%  %s\n",$1,$2,substr($0,index($0,$3))}'

sub "Počty instancí"
for p in "Google Chrome" python node Electron; do
  c=$(pgrep -f "$p" 2>/dev/null | wc -l | tr -d ' ')
  [ "${c:-0}" -gt 0 ] && printf '  %-16s %s procesů\n' "$p" "$c"
done

sub "Naslouchající porty (lokální služby)"
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null \
  | awk 'NR>1{split($9,a,":"); print a[length(a)]"\t"$1}' | sort -n -u | head -30
echo "  celkem: $(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"

# ---------------------------------------------------------------- LAUNCHD
h "LAUNCHD"
sub "Login items"
osascript -e 'tell application "System Events" to get the name of every login item' 2>/dev/null \
  | tr ',' '\n' | sed 's/^ */  /'

sub "Uživatelské agenty (~/Library/LaunchAgents)"
n_run=0; n_fail=0
for f in ~/Library/LaunchAgents/*.plist; do
  [ -e "$f" ] || continue
  lbl=$(basename "$f" .plist)
  line=$(launchctl list 2>/dev/null | awk -v l="$lbl" '$3==l{print $1" "$2}')
  pid=${line%% *}; ex=${line##* }
  if [ -z "$line" ]; then st="neaktivní"
  elif [ "$pid" != "-" ]; then st="běží (PID $pid)"; n_run=$((n_run+1))
  elif [ "${ex:-0}" != "0" ]; then st="NAPOSLED SELHAL (exit $ex)"; n_fail=$((n_fail+1))
  else st="naplánováno"; fi
  printf '  %-45s %s\n' "$lbl" "$st"
done
printf '\n  trvale běží: %s   |   selhalo: %s\n' "$n_run" "$n_fail"
[ "$n_fail" -gt 0 ] && echo "  Selhávající job se v cyklu restartuje — žere CPU potichu. Buď opravit, nebo odstavit."

sub "Systémové (ne-Apple) agenty a démoni"
ls /Library/LaunchAgents/*.plist /Library/LaunchDaemons/*.plist 2>/dev/null \
  | grep -vi apple | sed 's|.*/|  |'

# ---------------------------------------------------------------- SIROTCI
h "SIROTCI"
echo "Zbytky po aplikacích, které na disku už nejsou. Tohle je spolehlivá kategorie A:"
echo "nic se nedoinstaluje, protože mateřská aplikace neexistuje."

sub "launchd plisty ukazující na neexistující program"
for f in ~/Library/LaunchAgents/*.plist /Library/LaunchAgents/*.plist /Library/LaunchDaemons/*.plist; do
  [ -e "$f" ] || continue
  prog=$(/usr/libexec/PlistBuddy -c "Print :Program" "$f" 2>/dev/null) \
    || prog=$(/usr/libexec/PlistBuddy -c "Print :ProgramArguments:0" "$f" 2>/dev/null)
  [ -n "${prog:-}" ] || continue
  case "$prog" in /*) ;; *) continue ;; esac
  [ -e "$prog" ] || printf '  %-55s -> chybí %s\n' "$f" "$prog"
done

sub "Containery bez nainstalované aplikace (jen >20 MB)"
for d in ~/Library/Containers/*/; do
  id=$(basename "$d")
  case "$id" in com.apple.*|*-*-*-*-*) continue ;; esac
  kb=$(timeout 20 du -skx "$d" 2>/dev/null | cut -f1); [ "${kb:-0}" -gt 20480 ] || continue
  if [ -z "$(timeout 15 mdfind "kMDItemCFBundleIdentifier == '$id'" 2>/dev/null | head -1)" ]; then
    printf '  %-8s %s  (žádná aplikace s tímto bundle ID)\n' "$(sz "$d")" "$id"
  fi
done

sub "Updatery bez mateřské aplikace"
if [ -e /Library/LaunchAgents/com.microsoft.update.agent.plist ] \
   && [ -z "$(ls -d /Applications/Microsoft*.app 2>/dev/null)" ]; then
  echo "  Microsoft AutoUpdate běží, ale žádná aplikace Microsoftu není nainstalovaná."
fi
if [ -e /Library/LaunchAgents/com.google.keystone.agent.plist ] \
   && [ -z "$(ls -d /Applications/Google*.app /Applications/Chrome*.app 2>/dev/null)" ]; then
  echo "  Google Keystone běží, ale žádná aplikace Googlu není nainstalovaná."
fi

sub "Audio pluginy odinstalovaných aplikací"
ls -d /Library/Audio/Plug-Ins/HAL/*.driver 2>/dev/null | while read -r drv; do
  base=$(basename "$drv" .driver)
  case "$base" in
    MSTeams*) [ -z "$(ls -d /Applications/Microsoft*Teams*.app 2>/dev/null)" ] \
                && printf '  %-8s %s  (Teams není nainstalovaný)\n' "$(sz "$drv")" "$drv" ;;
    ZoomAudioDevice) [ -d /Applications/zoom.us.app ] || printf '  %-8s %s  (Zoom není nainstalovaný)\n' "$(sz "$drv")" "$drv" ;;
  esac
done

printf '\n---\nSken hotov. Nic nebylo smazáno ani vypnuto.\n'
