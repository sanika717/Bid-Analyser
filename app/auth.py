from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import DB_PATH, EMAIL_LOG_DIR, JWT_SECRET, PASSWORD_RESET_URL

security = HTTPBearer(auto_error=False)

HEADER = {"alg": "HS256", "typ": "JWT"}


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _encode_segment(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode("utf-8")
    segment = base64.urlsafe_b64encode(raw).rstrip(b"=")
    return segment.decode("utf-8")


def _decode_segment(segment: str) -> dict:
    padded = segment + "=" * (-len(segment) % 4)
    raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
    return json.loads(raw.decode("utf-8"))


def _sign(message: str) -> str:
    signature = hmac.new(JWT_SECRET.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).rstrip(b"=").decode("utf-8")


def init_auth_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT,
            role TEXT,
            password_hash TEXT,
            created_at TEXT
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS password_resets (
            token TEXT PRIMARY KEY,
            email TEXT,
            expires_at TEXT,
            used INTEGER DEFAULT 0
        )
        """
    )
    cur.execute("SELECT email FROM users WHERE email = 'admin@tce.com'")
    if not cur.fetchone():
        password_hash = _hash_password("TCEadmin123!")
        cur.execute(
            "INSERT INTO users (email, name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            ("admin@tce.com", "TCE Admin", "admin", password_hash, datetime.now(timezone.utc).isoformat()),
        )
    conn.commit()
    conn.close()


def get_user(email: str) -> Optional[dict]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT email, name, role, password_hash FROM users WHERE email = ?", (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {"email": row["email"], "name": row["name"], "role": row["role"], "password_hash": row["password_hash"]}


def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user(email)
    if not user:
        return None
    if hmac.compare_digest(user["password_hash"], _hash_password(password)):
        return {"email": user["email"], "name": user["name"], "role": user["role"]}
    return None


def create_user(email: str, password: str, name: str, role: str = "user") -> dict:
    password_hash = _hash_password(password)
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (email, name, role, password_hash, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return {"email": email, "name": name, "role": role}


def create_auth_token(email: str, name: str, role: str, hours: int = 8) -> str:
    payload = {
        "sub": email,
        "name": name,
        "role": role,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=hours)).timestamp()),
    }
    segments = [_encode_segment(HEADER), _encode_segment(payload)]
    signing_input = ".".join(segments)
    segments.append(_sign(signing_input))
    return ".".join(segments)


def get_user_by_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header = _decode_segment(parts[0])
        payload = _decode_segment(parts[1])
        signature = parts[2]
        if _sign(".".join(parts[:2])) != signature:
            return None
        if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
            return None
        return {"email": payload.get("sub"), "name": payload.get("name"), "role": payload.get("role")}
    except Exception:
        return None


def create_password_reset(email: str) -> str:
    token = os.urandom(24).hex()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO password_resets (token, email, expires_at, used) VALUES (?, ?, ?, 0)",
        (token, email, expires_at),
    )
    conn.commit()
    conn.close()
    return token


def get_password_reset(token: str) -> Optional[dict]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT token, email, expires_at, used FROM password_resets WHERE token = ?", (token,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def mark_password_reset_used(token: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE password_resets SET used = 1 WHERE token = ?", (token,))
    conn.commit()
    conn.close()


def update_password_hash(email: str, password: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash = ? WHERE email = ?", (_hash_password(password), email))
    conn.commit()
    conn.close()


def send_password_reset_email(email: str, token: str) -> str:
    EMAIL_LOG_DIR.mkdir(parents=True, exist_ok=True)
    link = f"{PASSWORD_RESET_URL}?token={token}"
    message = (
        f"To: {email}\n"
        f"Subject: TCE Bid Analyzer Password Reset\n\n"
        f"Use this link to reset your password:\n{link}\n"
        f"If you did not request this password reset, ignore this message.\n"
    )
    log_file = EMAIL_LOG_DIR / f"password_reset_{email.replace('@', '_').replace('.', '_')}.txt"
    log_file.write_text(message, encoding="utf-8")
    return message


def require_auth(credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = get_user_by_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user
