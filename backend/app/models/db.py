import sqlite3
from contextlib import contextmanager
from app.core.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('note', 'url')),
    title TEXT,
    source_url TEXT,
    raw_content TEXT,
    status TEXT NOT NULL DEFAULT 'processing' CHECK(status IN ('processing', 'ready', 'failed')),
    error_reason TEXT,
    char_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id);
"""

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)

@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()