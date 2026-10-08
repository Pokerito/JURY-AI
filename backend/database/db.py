import sqlite3
import os
import hashlib
import secrets
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "jury_ai.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                org_name TEXT,
                role TEXT DEFAULT 'analyst',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_type TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                filename TEXT NOT NULL,
                file_type TEXT,
                file_size INTEGER,
                status TEXT DEFAULT 'uploaded',
                text_content TEXT,
                summary TEXT,
                entities_json TEXT,
                score_json TEXT,
                created_at TEXT NOT NULL
            );
        """)
        
        # Ensure role column exists if upgrading an existing database
        try:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'analyst'")
            conn.commit()
        except sqlite3.OperationalError:
            pass # already exists

    # Pre-seed the 4 Project Admins
    seed_admins()

def seed_admins():
    admin_team = [
        {"name": "Gaurav Jha", "email": "gjha5757@gmail.com", "role": "admin", "org": "DSATM CSE (Lead)"},
        {"name": "Kalash Verma", "email": "kalashkumarverma72@gmail.com", "role": "admin", "org": "DSATM CSE (Backend & AI)"},
        {"name": "Krish Patel", "email": "mr.kpatel3008@gmail.com", "role": "admin", "org": "DSATM CSE (RAG Pipeline)"},
        {"name": "Komal Raj", "email": "sjckomalraj26@gmail.com", "role": "admin", "org": "DSATM CSE (Frontend & UI)"},
        # Aliases for convenience
        {"name": "Kalash", "email": "kalash@jury.ai", "role": "admin", "org": "DSATM CSE (Backend & AI)"},
        {"name": "Krish", "email": "krish@jury.ai", "role": "admin", "org": "DSATM CSE (RAG Pipeline)"},
        {"name": "Komal", "email": "komal@jury.ai", "role": "admin", "org": "DSATM CSE (Frontend & UI)"},
    ]
    for admin in admin_team:
        try:
            create_user(
                email=admin["email"],
                password="password123",
                full_name=admin["name"],
                org_name=admin["org"],
                role=admin["role"]
            )
        except Exception:
            pass
        except Exception:
            pass

def create_user(email: str, password: str, full_name: str = "", org_name: str = "", role: str = "analyst") -> dict:
    pw_hash = hash_password(password)
    now = datetime.utcnow().isoformat()
    clean_email = email.strip().lower()
    clean_name = full_name.strip() if full_name else clean_email.split('@')[0].capitalize()
    clean_org = org_name.strip() if org_name else "DSATM"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role FROM users WHERE LOWER(email) = ?", (clean_email,))
        existing = cursor.fetchone()
        if existing:
            user_id = existing["id"]
            # Preserve existing admin role if already admin
            user_role = existing["role"] if existing["role"] == "admin" else role
            cursor.execute(
                "UPDATE users SET password_hash = ?, full_name = ?, org_name = ?, role = ? WHERE id = ?",
                (pw_hash, clean_name, clean_org, user_role, user_id)
            )
            conn.commit()
            return {"id": user_id, "email": clean_email, "full_name": clean_name, "org_name": clean_org, "role": user_role, "created_at": now}

        user_id = secrets.token_hex(16)
        cursor.execute(
            "INSERT INTO users (id, email, password_hash, full_name, org_name, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, clean_email, pw_hash, clean_name, clean_org, role, now)
        )
        conn.commit()
    return {"id": user_id, "email": clean_email, "full_name": clean_name, "org_name": clean_org, "role": role, "created_at": now}

def authenticate_user(email_or_name: str, password: str):
    pw_hash = hash_password(password)
    ident = email_or_name.strip().lower()
    with get_db() as conn:
        cursor = conn.cursor()
        # 1. Exact match by email or name with password hash
        cursor.execute("""
            SELECT id, email, full_name, org_name, role, created_at 
            FROM users 
            WHERE (LOWER(email) = ? OR LOWER(full_name) = ?) AND password_hash = ?
        """, (ident, ident, pw_hash))
        row = cursor.fetchone()
        if row:
            return dict(row)

        # 2. Master demo password fallback for review convenience
        if password in ["password123", "password", "admin123"]:
            cursor.execute("""
                SELECT id, email, full_name, org_name, role, created_at 
                FROM users 
                WHERE LOWER(email) = ? OR LOWER(full_name) = ?
            """, (ident, ident))
            demo_row = cursor.fetchone()
            if demo_row:
                return dict(demo_row)
    return None

def create_tokens(user_id: str) -> dict:
    access_token = secrets.token_urlsafe(32)
    refresh_token = secrets.token_urlsafe(48)
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tokens (token, user_id, token_type, created_at) VALUES (?, ?, 'access', ?)", (access_token, user_id, now))
        cursor.execute("INSERT INTO tokens (token, user_id, token_type, created_at) VALUES (?, ?, 'refresh', ?)", (refresh_token, user_id, now))
        conn.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

def get_user_by_token(token: str):
    if not token:
        return None
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.email, u.full_name, u.org_name, u.role, u.created_at 
            FROM users u
            JOIN tokens t ON u.id = t.user_id
            WHERE t.token = ? AND t.token_type = 'access'
        """, (token,))
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def refresh_tokens(refresh_token: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM tokens WHERE token = ? AND token_type = 'refresh'", (refresh_token,))
        row = cursor.fetchone()
        if not row:
            return None
        user_id = row['user_id']
    return create_tokens(user_id)

def add_document(doc_id: str, filename: str, file_type: str, file_size: int, text_content: str, user_id: str = None) -> dict:
    now = datetime.utcnow().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (id, user_id, filename, file_type, file_size, status, text_content, created_at)
            VALUES (?, ?, ?, ?, ?, 'uploaded', ?, ?)
        """, (doc_id, user_id, filename, file_type, file_size, text_content, now))
        conn.commit()
    return {
        "id": doc_id,
        "filename": filename,
        "file_type": file_type,
        "file_size": file_size,
        "status": "uploaded",
        "created_at": now
    }

def get_documents(user_id: str = None, page: int = 1, page_size: int = 20) -> dict:
    offset = (page - 1) * page_size
    with get_db() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT COUNT(*) as cnt FROM documents WHERE user_id = ? OR user_id IS NULL", (user_id,))
            total = cursor.fetchone()['cnt']
            cursor.execute("""
                SELECT id, filename, file_type, file_size, status, created_at
                FROM documents
                WHERE user_id = ? OR user_id IS NULL
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (user_id, page_size, offset))
        else:
            cursor.execute("SELECT COUNT(*) as cnt FROM documents")
            total = cursor.fetchone()['cnt']
            cursor.execute("""
                SELECT id, filename, file_type, file_size, status, created_at
                FROM documents
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (page_size, offset))
        rows = cursor.fetchall()
        items = [dict(r) for r in rows]
    total_pages = max(1, (total + page_size - 1) // page_size)
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

def get_document(doc_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            if d.get('entities_json'):
                try:
                    d['entities'] = json.loads(d['entities_json'])
                except Exception:
                    d['entities'] = None
            if d.get('score_json'):
                try:
                    d['risk_score'] = json.loads(d['score_json'])
                except Exception:
                    d['risk_score'] = None
            return d
    return None

def update_document_analysis(doc_id: str, summary: str = None, entities: dict = None, score_data: dict = None, status: str = 'analyzed'):
    with get_db() as conn:
        cursor = conn.cursor()
        entities_json = json.dumps(entities) if entities else None
        score_json = json.dumps(score_data) if score_data else None
        cursor.execute("""
            UPDATE documents 
            SET summary = COALESCE(?, summary),
                entities_json = COALESCE(?, entities_json),
                score_json = COALESCE(?, score_json),
                status = ?
            WHERE id = ?
        """, (summary, entities_json, score_json, status, doc_id))
        conn.commit()

def delete_document(doc_id: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()

init_db()
