import sqlite3
from pathlib import Path
from typing import List, Optional
import json

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "jobs.sqlite"


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
            output TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def create_job(job_id: str, files: List[str], template: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO jobs (id, files, template, status, output) VALUES (?, ?, ?, ?, ?)",
        (job_id, json.dumps(files), template, "created", None),
    )
    conn.commit()
    conn.close()


def update_status(job_id: str, status: str, output: Optional[str] = None):
    conn = _get_conn()
    cur = conn.cursor()
    if output is None:
        cur.execute("UPDATE jobs SET status=? WHERE id=?", (status, job_id))
    else:
        cur.execute("UPDATE jobs SET status=?, output=? WHERE id=?", (status, output, job_id))
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
