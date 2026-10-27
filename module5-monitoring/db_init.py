"""Database setup (course lesson 05 + 08), with a SQLite / PostgreSQL switch.

The course runs PostgreSQL in Docker. Lesson 07 notes that without Grafana
you can use SQLite and skip Docker, which is what we do by default because
Docker is not installed on this machine.

    DB_BACKEND=sqlite    (default) -> monitoring.db file next to this script
    DB_BACKEND=postgres  -> course setup: Postgres on localhost:5432
                            (needs Docker + `uv add "psycopg[binary]"`)

The SQL below is the course's PostgreSQL SQL. `sql()` translates the few
Postgres-only bits for SQLite.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", str(Path(__file__).with_name("monitoring.db")))

DB_TIMEZONE = datetime.now().astimezone().tzinfo


def get_db_connection():
    if DB_BACKEND == "postgres":
        import psycopg

        return psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            dbname=os.getenv("POSTGRES_DB", "course_assistant"),
            user=os.getenv("POSTGRES_USER", "user"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
        )

    conn = sqlite3.connect(SQLITE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def sql(query):
    """Course SQL is written for PostgreSQL; adapt it when running on SQLite."""
    if DB_BACKEND == "postgres":
        return query
    return (
        query.replace("%s", "?")
        .replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
        .replace("TIMESTAMP WITH TIME ZONE", "TEXT")
    )


def now_value():
    """Timezone-aware timestamp; SQLite stores it as ISO text."""
    ts = datetime.now(DB_TIMEZONE)
    return ts if DB_BACKEND == "postgres" else ts.isoformat()


def init_db(drop=False):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if drop:
            cur.execute("DROP TABLE IF EXISTS feedback")
            cur.execute("DROP TABLE IF EXISTS conversations")

        cur.execute(sql("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                course TEXT NOT NULL,
                model TEXT NOT NULL,
                instructions TEXT NOT NULL,
                prompt TEXT NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                response_time FLOAT NOT NULL,
                cost FLOAT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """))
        conn.commit()
    finally:
        conn.close()


def init_feedback():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS feedback")
        cur.execute(sql("""
            CREATE TABLE feedback (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER REFERENCES conversations(id),
                source TEXT NOT NULL,
                relevance TEXT,
                explanation TEXT,
                score INTEGER,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL
            )
        """))
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    print(f"Backend: {DB_BACKEND}" + (f" ({SQLITE_PATH})" if DB_BACKEND == "sqlite" else ""))
    print(f"Using timezone: {DB_TIMEZONE}")
    init_db(drop="--drop" in sys.argv)
    init_feedback()
    print("Database initialized")
