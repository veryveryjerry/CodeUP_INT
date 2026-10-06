import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SymbolIndex:
    def __init__(self, db_path: str = "symbol_index.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS symbols (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                line_start INTEGER,
                line_end INTEGER,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                target_id INTEGER,
                rel_type TEXT,
                FOREIGN KEY(source_id) REFERENCES symbols(id),
                FOREIGN KEY(target_id) REFERENCES symbols(id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_symbol(self, name: str, symbol_type: str, file_path: str, line_start: int, line_end: int, metadata: str = "{}") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM symbols WHERE name = ? AND file_path = ? AND type = ?
        ''', (name, file_path, symbol_type))
        row = cursor.fetchone()
        
        if row:
            cursor.execute('''
                UPDATE symbols SET line_start=?, line_end=?, metadata=? WHERE id=?
            ''', (line_start, line_end, metadata, row[0]))
            symbol_id = row[0]
        else:
            cursor.execute('''
                INSERT INTO symbols (name, type, file_path, line_start, line_end, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, symbol_type, file_path, line_start, line_end, metadata))
            symbol_id = cursor.lastrowid
            
        conn.commit()
        conn.close()
        return symbol_id

    def add_relationship(self, source_id: int, target_id: int, rel_type: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO relationships (source_id, target_id, rel_type)
            VALUES (?, ?, ?)
        ''', (source_id, target_id, rel_type))
        conn.commit()
        conn.close()

    def find_symbol(self, name: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM symbols WHERE name LIKE ?', (f'%{name}%',))
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            result.append({
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "file_path": row[3],
                "line_start": row[4],
                "line_end": row[5],
                "metadata": row[6]
            })
        return result

    def find_usages(self, symbol_name: str) -> List[Dict[str, Any]]:
        return []

    def find_definition(self, name: str) -> List[Dict[str, Any]]:
        return self.find_symbol(name)
