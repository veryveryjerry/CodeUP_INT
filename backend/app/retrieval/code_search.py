import sqlite3
import subprocess
import logging
from typing import List, Dict, Any
from .semantic import SemanticRetrieval

logger = logging.getLogger(__name__)

class CodeSearch:
    def __init__(self, db_path: str = "search.db"):
        self.db_path = db_path
        self._init_db()
        self.semantic = SemanticRetrieval()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS code_fts USING fts5(
                file_path, content
            )
        ''')
        conn.commit()
        conn.close()

    def index_file(self, file_path: str, content: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO code_fts (file_path, content) VALUES (?, ?)
        ''', (file_path, content))
        conn.commit()
        conn.close()

    def keyword_search(self, query: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT file_path, snippet(code_fts, 1, '<b>', '</b>', '...', 64) 
            FROM code_fts WHERE content MATCH ? ORDER BY rank LIMIT 10
        ''', (query,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{"file": row[0], "snippet": row[1]} for row in rows]

    def regex_search(self, query: str, repo_path: str) -> List[Dict[str, Any]]:
        try:
            result = subprocess.run(
                ["rg", "-n", "--json", query, repo_path],
                capture_output=True,
                text=True
            )
            matches = []
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                try:
                    import json
                    data = json.loads(line)
                    if data.get("type") == "match":
                        match_data = data.get("data", {})
                        matches.append({
                            "file": match_data.get("path", {}).get("text"),
                            "line": match_data.get("line_number"),
                            "snippet": match_data.get("lines", {}).get("text", "").strip()
                        })
                except json.JSONDecodeError:
                    pass
            return matches
        except FileNotFoundError:
            logger.error("ripgrep (rg) not found.")
            return []

    def search(self, query: str, repo_path: str) -> List[Dict[str, Any]]:
        kw_results = self.keyword_search(query)
        rg_results = self.regex_search(query, repo_path)
        sem_results = self.semantic.search_code(query)
        
        combined = {
            "keyword": kw_results,
            "regex": rg_results,
            "semantic": sem_results
        }
        return combined
