#!/bin/bash
# Watchdog pro download_transcripts.py
# Každých 5 minut zkontroluje jestli skript běží — pokud ne, restartuje ho.
# Použití: bash watchdog.sh &

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/watchdog.log"
DOWNLOAD_LOG="$DIR/download.log"
PYTHON="/usr/bin/python3"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') $1" | tee -a "$LOG"
}

log "Watchdog spuštěn (DIR: $DIR)"

while true; do
    if ! pgrep -f "download_transcripts.py" > /dev/null 2>&1; then
        log "Skript neběží — restartuji"
        cd "$DIR" && $PYTHON download_transcripts.py >> "$DOWNLOAD_LOG" 2>&1 &
        log "Spuštěno (PID: $!)"
    fi
    sleep 300
done
