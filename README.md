# OSINT Telegram Bot — safe public-data MVP

Python 3.11+ / aiogram 3 / SQLite.

This project implements the Telegram UI, database, admin panel, search history,
tracking records, self-check, privacy/help sections, and public-chat lookup.

A normal Telegram Bot API bot cannot search Telegram's entire global user/group/
message database. Global `/human`, `/text`, `/search`, historical-name tracking
and large-scale message indexing therefore need a legitimate public-data source
or an authorized indexing pipeline. The source adapter is intentionally left
pluggable.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add the BotFather token to `.env`, then:

```bash
python bot.py
```

Set admin IDs in `ADMIN_IDS`.

The project does not collect passwords/login codes, read private chats, access
hidden contacts, or bypass Telegram privacy controls.
