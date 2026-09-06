import sqlite3
from pathlib import Path
from config import settings

def connect():
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn

async def init_db():
    conn = connect()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        language TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_activity TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        query TEXT NOT NULL,
        search_type TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        target TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS name_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        display_name TEXT NOT NULL,
        observed_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS public_chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        username TEXT,
        title TEXT,
        chat_type TEXT,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

def upsert_user(user):
    conn = connect()
    conn.execute("""
        INSERT INTO users(telegram_id, username, first_name, language)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
          username=excluded.username,
          first_name=excluded.first_name,
          language=excluded.language,
          last_activity=CURRENT_TIMESTAMP
    """, (user.id, user.username, user.first_name, user.language_code))
    conn.commit()
    conn.close()

def add_search(user_id, query, search_type):
    conn = connect()
    conn.execute("INSERT INTO searches(user_id, query, search_type) VALUES (?, ?, ?)",
                 (user_id, query, search_type))
    conn.commit()
    conn.close()

def add_tracking(user_id, target):
    conn = connect()
    conn.execute("INSERT INTO tracking(user_id, target) VALUES (?, ?)", (user_id, target))
    conn.commit()
    conn.close()

def add_name_observation(telegram_id, display_name):
    conn = connect()
    conn.execute("INSERT INTO name_history(telegram_id, display_name) VALUES (?, ?)",
                 (telegram_id, display_name))
    conn.commit()
    conn.close()

def stats():
    conn = connect()
    data = {
        "users": conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "searches": conn.execute("SELECT COUNT(*) FROM searches").fetchone()[0],
        "tracking": conn.execute("SELECT COUNT(*) FROM tracking WHERE status='active'").fetchone()[0],
    }
    conn.close()
    return data

def all_user_ids():
    conn = connect()
    rows = conn.execute("SELECT telegram_id FROM users").fetchall()
    conn.close()
    return [r[0] for r in rows]
