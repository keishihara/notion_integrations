#!/bin/bash

cd /mnt/wdblue1/kc/projects/personal/notion_integrations

mkdir -p weekly_notes/logs

# Set log file's name without colons
LOGFILE="weekly_notes/logs/add_weekly_note_next_weeek$(date '+%Y-%m-%dT%H%M%S').log"

/mnt/wdblue1/kc/projects/personal/notion_integrations/env/bin/python weekly_notes/add_weekly_note.py --next-week >> "$LOGFILE" 2>&1
