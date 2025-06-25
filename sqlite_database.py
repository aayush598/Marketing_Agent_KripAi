# sqlite_database.py
import sqlite3
from datetime import datetime
from typing import Optional

DB_NAME = "recommendations.db"

class SQLiteDB:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                budget TEXT,
                timeline TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                recommendation TEXT,
                created_at TEXT,
                FOREIGN KEY(project_id) REFERENCES projects(id)
            )
        """)
        self.conn.commit()

    def save_project(self, description: str, budget: str, timeline: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO projects (description, budget, timeline, created_at)
            VALUES (?, ?, ?, ?)
        """, (description, budget, timeline, datetime.now().isoformat()))
        self.conn.commit()
        return cursor.lastrowid

    def save_recommendation(self, project_id: int, recommendation: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO recommendations (project_id, recommendation, created_at)
            VALUES (?, ?, ?)
        """, (project_id, recommendation, datetime.now().isoformat()))
        self.conn.commit()

    def get_cached_recommendation(self, description: str, budget: str, timeline: str) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT r.recommendation
            FROM projects p
            JOIN recommendations r ON p.id = r.project_id
            WHERE p.description = ? AND p.budget = ? AND p.timeline = ?
            ORDER BY r.created_at DESC
            LIMIT 1
        """, (description, budget, timeline))
        row = cursor.fetchone()
        return row[0] if row else None
