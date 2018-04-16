# msgbot
A Python Discord selfbot that stores user messages in individual .csv (comma-separated value) files.

Currently persists a timestamp, Author ID, Guild ID (where applicable), channel ID, and message contents. Private messages are persisted in files corresponding to recipient channel IDs, while guild messages are stored in files corresponding to the guild ID.

## Usage
In the same directory as `bot.py` (Mac/Linux):
- `$ MSGBOT_EMAIL=<email> MSGBOT_PASS=<password> python3.py`
- `$ MSGBOT_TOKEN=<bot token> python3 bot.py`

Or, on Windows:
```cmd
> SET MSGBOT_EMAIL=<email> && SET MSGBOT_PASS=<pass>
> REM or...
> SET MSGBOT_TOKEN=<token>
>
> python3 bot.py
```

if `MSGBOT_LOG` is set, the bot will log; if empty or zero, then it won't.
