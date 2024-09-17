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

# Runs every Sunday at 00:00
0 0 * * 0 /path/to/notion_integrations/weekly_notes/run_add_weekly_note.sh
```
