# Notion Integrations


## Weekly Notes
The `weekly_notes/add_weekly_note.py` script automates the creation of a weekly note page in your Notion database. It can be scheduled to run automatically using cron.

```bash
python weekly_notes/add_weekly_note.py
```


### Scheduling with Cron
Edit your `crontab` to schedule the script. For example:
```
$ crontab -e

# Example 1: Runs every Sunday at 00:00
0 0 * * 0 /path/to/notion_integrations/weekly_notes/run_add_weekly_note_next_week.sh

# Example 2: Runs every Friday at 8:00
0 8 * * 5 /path/to/notion_integrations/weekly_notes/run_add_weekly_note_next_week.sh
```
