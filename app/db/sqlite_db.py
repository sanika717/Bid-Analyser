import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "storage" / "jobs" / "jobs.sqlite"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            files TEXT,
            template TEXT,
            status TEXT,
            output TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    cur.execute("PRAGMA table_info(jobs)")
    columns = {row[1] for row in cur.fetchall()}
    if "created_at" not in columns:
        cur.execute("ALTER TABLE jobs ADD COLUMN created_at TEXT")
    if "updated_at" not in columns:
        cur.execute("ALTER TABLE jobs ADD COLUMN updated_at TEXT")
    conn.commit()
    conn.close()


def create_job(job_id: str, files: List[str], template: str):
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO jobs (id, files, template, status, output, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (job_id, json.dumps(files), template, "created", None, timestamp, timestamp),
    )
    conn.commit()
    conn.close()


def update_status(job_id: str, status: str, output: Optional[str] = None):
    timestamp = datetime.now(timezone.utc).isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    if output is None:
        cur.execute("UPDATE jobs SET status=?, updated_at=? WHERE id=?", (status, timestamp, job_id))
    else:
        cur.execute("UPDATE jobs SET status=?, output=?, updated_at=? WHERE id=?", (status, output, timestamp, job_id))
    conn.commit()
    conn.close()


def get_job(job_id: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def get_jobs(limit: int = 10):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY created_at DESC, id DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows
