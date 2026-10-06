import sqlite3
from typing import List, Dict, Any, Optional
from pathlib import Path
from .config import settings
from .models import TaskState
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: Path = settings.DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tasks table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                repo_url TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                state TEXT NOT NULL,
                progress REAL DEFAULT 0,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Repositories table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS repositories (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                branch TEXT NOT NULL,
                commit_hash TEXT
            )
            """)
            
            # Files table with FTS5
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id TEXT,
                path TEXT NOT NULL,
                language TEXT,
                content TEXT,
                FOREIGN KEY (repo_id) REFERENCES repositories(id)
            )
            """)
            
            cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                path, content, content='files', content_rowid='id'
            )
            """)
            
            # Triggers to keep FTS table in sync
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS files_ai AFTER INSERT ON files BEGIN
                INSERT INTO files_fts(rowid, path, content) VALUES (new.id, new.path, new.content);
            END;
            """)
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS files_ad AFTER DELETE ON files BEGIN
                INSERT INTO files_fts(files_fts, rowid, path, content) VALUES('delete', old.id, old.path, old.content);
            END;
            """)
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS files_au AFTER UPDATE ON files BEGIN
                INSERT INTO files_fts(files_fts, rowid, path, content) VALUES('delete', old.id, old.path, old.content);
                INSERT INTO files_fts(rowid, path, content) VALUES (new.id, new.path, new.content);
            END;
            """)

            # Symbols
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                id TEXT PRIMARY KEY,
                file_id INTEGER,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                start_line INTEGER,
                end_line INTEGER,
                FOREIGN KEY (file_id) REFERENCES files(id)
            )
            """)

            # Relationships
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT,
                target_id TEXT,
                type TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES symbols(id),
                FOREIGN KEY (target_id) REFERENCES symbols(id)
            )
            """)
            
            # Tests, Patches, Evidence, AgentRuns...
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                test_name TEXT,
                passed BOOLEAN,
                output TEXT,
                duration REAL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS patches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                file_path TEXT,
                original_code TEXT,
                replacement_code TEXT,
                applied BOOLEAN,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                type TEXT,
                description TEXT,
                score REAL,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT,
                event_type TEXT,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
            """)
            conn.commit()

    def create_task(self, task_id: str, repo_url: str, issue_description: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO tasks (id, repo_url, issue_description, state, message) VALUES (?, ?, ?, ?, ?)",
                (task_id, repo_url, issue_description, TaskState.PENDING.value, "Task created")
            )
            conn.commit()
            
    def update_task_state(self, task_id: str, state: str, progress: float, message: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET state = ?, progress = ?, message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (state, progress, message, task_id)
            )
            conn.commit()
            
    def get_task(self, task_id: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if row:
                # Format datetime fields if needed, returning dict
                return dict(row)
            return None

    def search_code(self, query: str) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT path, snippet(files_fts, -1, '<b>', '</b>', '...', 10) as snippet FROM files_fts WHERE files_fts MATCH ?",
                (query,)
            )
            return [dict(row) for row in cursor.fetchall()]

db = DatabaseManager()
