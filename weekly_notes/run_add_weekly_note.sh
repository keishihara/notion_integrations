#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
source env/bin/activate

mkdir -p weekly_notes/logs

LOGFILE="weekly_notes/logs/add_weekly_note_$(date '+%Y-%m-%dT%H%M%S').log"

# Add weekly note
python weekly_notes/add_weekly_note.py >> "$LOGFILE" 2>&1

# Send notification to LINE
python weekly_notes/send_line_notification.py "$LOGFILE"
