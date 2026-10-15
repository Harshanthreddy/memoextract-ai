import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from frontend.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Open a thread-safe connection with dict-like row access"""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize SQLite tables and indexes"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_hash TEXT,
        filename TEXT NOT NULL,
        file_size_bytes INTEGER DEFAULT 0,
        file_type TEXT,
        engine TEXT,
        status TEXT DEFAULT 'SUCCESS',
        student_name TEXT,
        roll_no TEXT,
        institution TEXT,
        result TEXT,
        sgpa TEXT,
        percentage REAL DEFAULT 0.0,
        total_obtained REAL DEFAULT 0.0,
        total_max REAL DEFAULT 0.0,
        is_broadsheet INTEGER DEFAULT 0,
        candidate_count INTEGER DEFAULT 1,
        extracted_data_json TEXT,
        validation_warnings_json TEXT,
        processing_time_sec REAL DEFAULT 0.0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(file_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_created ON documents(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_student ON documents(student_name, roll_no)")
    conn.commit()
    conn.close()


def save_extracted_document(
    filename: str,
    file_bytes: bytes,
    engine: str,
    data: Dict[str, Any],
    validation_warnings: List[str],
    processing_time_sec: float,
    status: str = "SUCCESS",
    file_hash: Optional[str] = None
) -> int:
    """Save an extraction record into SQLite and return its new row ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    is_broadsheet = 1 if data.get("is_broadsheet") else 0
    candidate_count = data.get("total_candidates", 1) if is_broadsheet else 1

    # Extract primary student details for fast searching/filtering
    primary = data.get("primary", data) if is_broadsheet else data

    student_name = ""
    if isinstance(primary.get("name"), dict):
        student_name = primary["name"].get("value", "")
    elif primary.get("name"):
        student_name = str(primary["name"])

    roll_no = ""
    if isinstance(primary.get("roll_no"), dict):
        roll_no = primary["roll_no"].get("value", "")
    elif primary.get("roll_no"):
        roll_no = str(primary["roll_no"])

    result_val = ""
    if isinstance(primary.get("result"), dict):
        result_val = primary["result"].get("value", "")
    elif primary.get("result"):
        result_val = str(primary["result"])

    sgpa_val = ""
    if isinstance(primary.get("sgpa"), dict):
        sgpa_val = primary["sgpa"].get("value", "")
    elif primary.get("sgpa"):
        sgpa_val = str(primary["sgpa"])

    institution = data.get("institution", "")

    # Calculate numeric percentage / totals if available
    total_obt = 0.0
    total_max = 0.0
    percentage = 0.0

    for s in primary.get("subjects", []):
        try:
            total_obt += float(s.get("obtained", 0))
            total_max += float(s.get("max", 100))
        except (ValueError, TypeError):
            pass

    if total_max > 0:
        percentage = round((total_obt / total_max) * 100, 2)

    # Determine status
    if validation_warnings and any(w.startswith("Error") or "Missing" in w for w in validation_warnings):
        status = "REVIEW_NEEDED"

    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO documents (
        file_hash, filename, file_size_bytes, file_type, engine,
        status, student_name, roll_no, institution, result,
        sgpa, percentage, total_obtained, total_max, is_broadsheet,
        candidate_count, extracted_data_json, validation_warnings_json,
        processing_time_sec, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        file_hash or "",
        filename,
        len(file_bytes),
        filename.split(".")[-1].upper() if "." in filename else "DOC",
        engine,
        status,
        student_name,
        roll_no,
        institution,
        result_val,
        sgpa_val,
        percentage,
        total_obt,
        total_max,
        is_broadsheet,
        candidate_count,
        json.dumps(data, ensure_ascii=False),
        json.dumps(validation_warnings, ensure_ascii=False),
        round(processing_time_sec, 2),
        now_iso
    ))

    doc_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def get_document_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve full document details and parsed JSON by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    item = dict(row)
    try:
        item["extracted_data"] = json.loads(item.get("extracted_data_json") or "{}")
    except Exception:
        item["extracted_data"] = {}

    try:
        item["validation_warnings"] = json.loads(item.get("validation_warnings_json") or "[]")
    except Exception:
        item["validation_warnings"] = []

    return item


def get_all_documents(
    search: str = "",
    engine_filter: str = "All",
    status_filter: str = "All",
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Query documents with filtering, search, and pagination"""
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if search.strip():
        term = f"%{search.strip()}%"
        conditions.append("(filename LIKE ? OR student_name LIKE ? OR roll_no LIKE ? OR institution LIKE ?)")
        params.extend([term, term, term, term])

    if engine_filter and engine_filter != "All":
        conditions.append("engine = ?")
        params.append(engine_filter)

    if status_filter and status_filter != "All":
        conditions.append("status = ?")
        params.append(status_filter)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
    SELECT id, filename, file_size_bytes, file_type, engine, status,
           student_name, roll_no, institution, result, sgpa, percentage,
           is_broadsheet, candidate_count, processing_time_sec, created_at
    FROM documents
    {where_clause}
    ORDER BY id DESC
    LIMIT ? OFFSET ?
    """
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def update_document_data(doc_id: int, updated_data: Dict[str, Any], validation_warnings: List[str]) -> bool:
    """Update extracted_data_json and validation warnings after user edits"""
    conn = get_db_connection()
    cursor = conn.cursor()

    is_broadsheet = 1 if updated_data.get("is_broadsheet") else 0
    primary = updated_data.get("primary", updated_data) if is_broadsheet else updated_data

    student_name = primary.get("name", {}).get("value", "") if isinstance(primary.get("name"), dict) else str(primary.get("name", ""))
    roll_no = primary.get("roll_no", {}).get("value", "") if isinstance(primary.get("roll_no"), dict) else str(primary.get("roll_no", ""))
    result_val = primary.get("result", {}).get("value", "") if isinstance(primary.get("result"), dict) else str(primary.get("result", ""))
    sgpa_val = primary.get("sgpa", {}).get("value", "") if isinstance(primary.get("sgpa"), dict) else str(primary.get("sgpa", ""))

    cursor.execute("""
    UPDATE documents
    SET student_name = ?, roll_no = ?, result = ?, sgpa = ?,
        extracted_data_json = ?, validation_warnings_json = ?,
        status = CASE WHEN status = 'FAILED' THEN 'SUCCESS' ELSE status END
    WHERE id = ?
    """, (
        student_name, roll_no, result_val, sgpa_val,
        json.dumps(updated_data, ensure_ascii=False),
        json.dumps(validation_warnings, ensure_ascii=False),
        doc_id
    ))
    conn.commit()
    conn.close()
    return True


def delete_document(doc_id: int) -> bool:
    """Delete a document record by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    return True


def clear_all_documents() -> bool:
    """Wipe all document history records from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents")
    conn.commit()
    conn.close()
    return True


def get_dashboard_stats() -> Dict[str, Any]:
    """Compute live KPI stats from database"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'SUCCESS'")
    success_docs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'REVIEW_NEEDED'")
    review_docs = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(processing_time_sec) FROM documents WHERE processing_time_sec > 0")
    avg_time_row = cursor.fetchone()[0]
    avg_time = round(avg_time_row, 2) if avg_time_row else 0.0

    cursor.execute("SELECT SUM(candidate_count) FROM documents")
    cand_row = cursor.fetchone()[0]
    total_candidates = cand_row if cand_row else total_docs

    success_rate = round((success_docs / total_docs * 100), 1) if total_docs > 0 else 0.0

    conn.close()

    return {
        "total_documents": total_docs,
        "successful_extractions": success_docs,
        "documents_for_review": review_docs,
        "average_processing_time": avg_time,
        "total_candidates": total_candidates,
        "success_rate": success_rate
    }


def get_analytics_metrics() -> Dict[str, Any]:
    """Compute aggregate analytics for charts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Engine distribution
    cursor.execute("SELECT engine, COUNT(*) FROM documents GROUP BY engine")
    engine_dist = dict(cursor.fetchall())

    # Result distribution (Pass / Fail / Distinction)
    cursor.execute("""
    SELECT 
        CASE 
            WHEN UPPER(result) LIKE '%DIST%' THEN 'Distinction'
            WHEN UPPER(result) LIKE '%FIRST%' THEN 'First Class'
            WHEN UPPER(result) LIKE '%PASS%' THEN 'Passed'
            WHEN UPPER(result) LIKE '%FAIL%' THEN 'Failed'
            ELSE 'Other'
        END as res_cat, COUNT(*) 
    FROM documents 
    WHERE result != '' AND result IS NOT NULL
    GROUP BY res_cat
    """)
    result_dist = dict(cursor.fetchall())

    # Activity by Date (Last 7 active entries)
    cursor.execute("""
    SELECT SUBSTR(created_at, 1, 10) as day, COUNT(*) 
    FROM documents 
    GROUP BY day 
    ORDER BY day DESC 
    LIMIT 7
    """)
    activity_timeline = dict(cursor.fetchall())

    conn.close()

    return {
        "engine_distribution": engine_dist,
        "result_distribution": result_dist,
        "activity_timeline": activity_timeline
    }
