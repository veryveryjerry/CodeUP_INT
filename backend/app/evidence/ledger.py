import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict

@dataclass
class EvidenceRecord:
    claim: str
    file: str
    symbol: str
    line_start: int
    line_end: int
    reason: str
    evidence_type: str  # ast, search, test, runtime, git, manifest

class EvidenceLedger:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim TEXT,
                file TEXT,
                symbol TEXT,
                line_start INTEGER,
                line_end INTEGER,
                reason TEXT,
                evidence_type TEXT
            )
        ''')
        self.conn.commit()

    def add_evidence(self, record: EvidenceRecord) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO evidence (claim, file, symbol, line_start, line_end, reason, evidence_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (record.claim, record.file, record.symbol, record.line_start, record.line_end, record.reason, record.evidence_type))
        self.conn.commit()

    def get_evidence_for_file(self, file: str) -> List[EvidenceRecord]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT claim, file, symbol, line_start, line_end, reason, evidence_type FROM evidence WHERE file = ?', (file,))
        return [EvidenceRecord(*row) for row in cursor.fetchall()]

    def get_evidence_for_claim(self, claim: str) -> List[EvidenceRecord]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT claim, file, symbol, line_start, line_end, reason, evidence_type FROM evidence WHERE claim = ?', (claim,))
        return [EvidenceRecord(*row) for row in cursor.fetchall()]

    def get_all_evidence(self) -> List[EvidenceRecord]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT claim, file, symbol, line_start, line_end, reason, evidence_type FROM evidence')
        return [EvidenceRecord(*row) for row in cursor.fetchall()]

    def validate_claims(self) -> bool:
        """Checks if all claims have at least one supporting evidence record."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT claim FROM evidence')
        claims = [row[0] for row in cursor.fetchall()]
        
        for claim in claims:
            if not self.get_evidence_for_claim(claim):
                return False
        return True

    def to_dict(self) -> List[Dict]:
        return [asdict(record) for record in self.get_all_evidence()]
        
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
