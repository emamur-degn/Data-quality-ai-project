import json
import sqlite3
from datetime import datetime, timezone

DB_PATH = "dataquality_history.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                filename TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                issues INTEGER NOT NULL,
                anomalies INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                report_json TEXT NOT NULL,
                ai_summary TEXT
            )
        """)

def save_run(filename, summary, issues, anomalies, ai_summary=""):
    report = json.dumps({"summary": summary, "issues": issues, "anomalies": anomalies}, ensure_ascii=False)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO analysis_runs
            (created_at, filename, total_rows, issues, anomalies, quality_score, report_json, ai_summary)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now(timezone.utc).isoformat(),
            filename,
            int(summary["total_rows"]),
            int(summary["issue_count"]),
            int(summary["anomaly_count"]),
            float(summary["quality_score"]),
            report,
            ai_summary
        ))
        return cur.lastrowid

def recent_runs(limit=20):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT id, created_at, filename, total_rows, issues, anomalies, quality_score
            FROM analysis_runs ORDER BY id DESC LIMIT ?
        """, (int(limit),)).fetchall()
    keys = ["run_id", "created_at", "filename", "rows", "issues", "anomalies", "quality_score"]
    return [dict(zip(keys, row)) for row in rows]
