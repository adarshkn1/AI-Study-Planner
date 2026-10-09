import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "study_planner.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hashes plain text password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    """Initializes SQLite database tables for multi-user persistent agent memory."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Check if legacy single-user database exists (settings table without user_id)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings'")
        if cursor.fetchone():
            cursor.execute("PRAGMA table_info(settings)")
            columns = [col['name'] for col in cursor.fetchall()]
            if 'user_id' not in columns:
                # Migrate by dropping old single-user tables to update schema cleanly
                cursor.execute("DROP TABLE IF EXISTS settings")
                cursor.execute("DROP TABLE IF EXISTS subjects")
                cursor.execute("DROP TABLE IF EXISTS daily_plan")
                cursor.execute("DROP TABLE IF EXISTS study_logs")
                cursor.execute("DROP TABLE IF EXISTS agent_decisions")

        # Table 0: Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Table 1: Settings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                exam_date TEXT NOT NULL,
                daily_hours INTEGER NOT NULL,
                max_daily_hours INTEGER NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Table 2: Subjects
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                score INTEGER NOT NULL,
                priority INTEGER DEFAULT 3,
                PRIMARY KEY (user_id, name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Table 3: Daily Plan (Planned Work)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_plan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                plan_date TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                planned_minutes INTEGER NOT NULL,
                UNIQUE(user_id, plan_date, subject_name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Table 4: Study Logs (Actual Work Completed)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS study_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                completed_minutes INTEGER NOT NULL,
                logged_at TEXT NOT NULL,
                UNIQUE(user_id, log_date, subject_name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Table 5: Agent Decisions Log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                trigger_event TEXT NOT NULL,
                reason TEXT NOT NULL,
                decision TEXT NOT NULL,
                constraint_applied TEXT NOT NULL,
                result TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

# --- USER AUTHENTICATION MEMORY FUNCTIONS ---

def register_user(username: str, password: str):
    """Registers a new user. Returns (success: bool, user_dict_or_error: dict/str)"""
    username_clean = username.strip().lower()
    if not username_clean:
        return False, "Username cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    pwd_hash = hash_password(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
            """, (username_clean, pwd_hash, datetime.now().isoformat()))
            conn.commit()
            user_id = cursor.lastrowid
            return True, {"id": user_id, "username": username_clean}
        except sqlite3.IntegrityError:
            return False, "Username is already taken. Please choose another username or log in."

def authenticate_user(username: str, password: str):
    """Authenticates user credentials. Returns user dict if valid, None if invalid."""
    username_clean = username.strip().lower()
    pwd_hash = hash_password(password)
    with get_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute("""
            SELECT id, username FROM users
            WHERE username = ? AND password_hash = ?
        """, (username_clean, pwd_hash)).fetchone()
        if row:
            return dict(row)
        return None

# --- USER-SCOPED PERSISTENCE FUNCTIONS ---

def save_settings(user_id: int, exam_date: str, daily_hours: int, max_daily_hours: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (user_id, exam_date, daily_hours, max_daily_hours, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                exam_date=excluded.exam_date,
                daily_hours=excluded.daily_hours,
                max_daily_hours=excluded.max_daily_hours,
                updated_at=excluded.updated_at
        """, (user_id, exam_date, daily_hours, max_daily_hours, datetime.now().isoformat()))
        conn.commit()

def load_settings(user_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        row = cursor.execute("SELECT * FROM settings WHERE user_id = ?", (user_id,)).fetchone()
        if row:
            return dict(row)
        return None

def save_subjects(user_id: int, subjects_data: list):
    """subjects_data = [{'name': 'Math', 'score': 45, 'priority': 4}, ...]"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE user_id = ?", (user_id,))
        for item in subjects_data:
            cursor.execute("""
                INSERT INTO subjects (user_id, name, score, priority)
                VALUES (?, ?, ?, ?)
            """, (user_id, item['name'], item['score'], item.get('priority', 3)))
        conn.commit()

def load_subjects(user_id: int) -> list:
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT name, score, priority FROM subjects WHERE user_id = ?", (user_id,)).fetchall()
        return [dict(r) for r in rows]

def save_daily_plan(user_id: int, plan_dict: dict):
    """plan_dict = {'2026-10-10': {'Math': 90, 'DSA': 60}}"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_plan WHERE user_id = ?", (user_id,))
        for plan_date, subjs in plan_dict.items():
            for subj, minutes in subjs.items():
                cursor.execute("""
                    INSERT INTO daily_plan (user_id, plan_date, subject_name, planned_minutes)
                    VALUES (?, ?, ?, ?)
                """, (user_id, plan_date, subj, minutes))
        conn.commit()

def load_daily_plan(user_id: int) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT plan_date, subject_name, planned_minutes FROM daily_plan WHERE user_id = ? ORDER BY plan_date", (user_id,)).fetchall()
        plan = {}
        for r in rows:
            p_date = r['plan_date']
            if p_date not in plan:
                plan[p_date] = {}
            plan[p_date][r['subject_name']] = r['planned_minutes']
        return plan

def log_subject_completion(user_id: int, log_date: str, subject_name: str, completed_minutes: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO study_logs (user_id, log_date, subject_name, completed_minutes, logged_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, log_date, subject_name) DO UPDATE SET
                completed_minutes=excluded.completed_minutes,
                logged_at=excluded.logged_at
        """, (user_id, log_date, subject_name, completed_minutes, datetime.now().isoformat()))
        conn.commit()

def load_study_logs(user_id: int) -> dict:
    """Returns logs grouped by date: {'2026-10-10': {'Math': 60, 'DSA': 30}}"""
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT log_date, subject_name, completed_minutes FROM study_logs WHERE user_id = ?", (user_id,)).fetchall()
        logs = {}
        for r in rows:
            d = r['log_date']
            if d not in logs:
                logs[d] = {}
            logs[d][r['subject_name']] = r['completed_minutes']
        return logs

def save_agent_decision(user_id: int, trigger_event: str, reason: str, decision: str, constraint_applied: str, result: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agent_decisions (user_id, timestamp, trigger_event, reason, decision, constraint_applied, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), trigger_event, reason, decision, constraint_applied, result))
        conn.commit()

def load_agent_decisions(user_id: int) -> list:
    with get_connection() as conn:
        cursor = conn.cursor()
        rows = cursor.execute("SELECT * FROM agent_decisions WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
        return [dict(r) for r in rows]

def clear_all_data(user_id: int = None):
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("DELETE FROM settings WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM subjects WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM daily_plan WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM study_logs WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM agent_decisions WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM settings")
            cursor.execute("DELETE FROM subjects")
            cursor.execute("DELETE FROM daily_plan")
            cursor.execute("DELETE FROM study_logs")
            cursor.execute("DELETE FROM agent_decisions")
        conn.commit()
