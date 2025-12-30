"""
Metadata Storage Database
SQLite-based persistent storage for extracted metadata with search capabilities
"""

import sqlite3
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import hashlib


DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data', 'metadata.db')
_DB_INITIALIZED = False


def _open_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def get_db_connection():
    """Get database connection, creating database if needed."""
    global _DB_INITIALIZED
    if not _DB_INITIALIZED:
        init_database()
        _DB_INITIALIZED = True
    return _open_connection()


def init_database():
    """Initialize database tables."""
    conn = _open_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE NOT NULL,
            file_hash TEXT NOT NULL,
            file_size INTEGER,
            file_mtime REAL,
            file_type TEXT,
            extracted_at TEXT,
            last_updated TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            file_id INTEGER,
            category TEXT,
            key TEXT,
            value TEXT,
            PRIMARY KEY (file_id, category, key),
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perceptual_hashes (
            file_id INTEGER PRIMARY KEY,
            phash TEXT,
            dhash TEXT,
            ahash TEXT,
            whash TEXT,
            blockhash TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            file_id INTEGER PRIMARY KEY,
            added_at TEXT,
            notes TEXT,
            tags TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS version_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            changed_at TEXT,
            change_type TEXT,
            category TEXT,
            key TEXT,
            old_value TEXT,
            new_value TEXT,
            FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_files_hash ON files(file_hash)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_files_type ON files(file_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_metadata_category ON metadata(category)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_metadata_key ON metadata(key)
    """)
    
    # Lightweight migration for older version_history schema
    cursor.execute("PRAGMA table_info(version_history)")
    columns = {row[1] for row in cursor.fetchall()}
    if "category" not in columns:
        cursor.execute("ALTER TABLE version_history ADD COLUMN category TEXT")
    if "key" not in columns:
        cursor.execute("ALTER TABLE version_history ADD COLUMN key TEXT")

    conn.commit()
    conn.close()


def file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def _stringify_value(value: Any) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)[:1000]
    return json.dumps(value, default=str)[:1000]


def _flatten_metadata(metadata: Dict[str, Any]) -> Dict[tuple, str]:
    flat: Dict[tuple, str] = {}
    for category, data in metadata.items():
        if not data or category.startswith("_"):
            continue
        if isinstance(data, dict):
            if data.get("_locked") is True:
                continue
            for key, value in data.items():
                if key.startswith("_") or value is None:
                    continue
                flat[(category, str(key))] = _stringify_value(value)
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value is None:
                            continue
                        flat[(f"{category}_{idx}", str(key))] = _stringify_value(value)
    return flat


def _record_changes(
    cursor: sqlite3.Cursor,
    file_id: int,
    changes: List[Dict[str, Any]],
    changed_at: str,
) -> None:
    for change in changes:
        cursor.execute(
            """
            INSERT INTO version_history (file_id, changed_at, change_type, category, key, old_value, new_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                file_id,
                changed_at,
                change["change_type"],
                change["category"],
                change["key"],
                change.get("old_value"),
                change.get("new_value"),
            ),
        )


def store_file_metadata(
    filepath: str,
    metadata: Dict[str, Any],
    perceptual_hashes: Optional[Dict[str, Any]] = None,
    is_favorite: bool = False,
) -> int:
    """
    Store or update file metadata in the database.

    Returns the file ID, or -1 on failure.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    file_path = os.path.abspath(filepath)
    file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
    file_mtime = os.path.getmtime(filepath) if os.path.exists(filepath) else 0
    file_type = Path(filepath).suffix.lower()
    file_hash_val = file_hash(filepath)
    now = datetime.now().isoformat()

    flat_metadata = _flatten_metadata(metadata)

    try:
        cursor.execute("SELECT id, file_hash FROM files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        if not row:
            cursor.execute(
                """
                INSERT INTO files (file_path, file_hash, file_size, file_mtime, file_type, extracted_at, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (file_path, file_hash_val, file_size, file_mtime, file_type, now, now),
            )
            file_id = cursor.lastrowid
            for (category, key), value in flat_metadata.items():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO metadata (file_id, category, key, value)
                    VALUES (?, ?, ?, ?)
                """,
                    (file_id, category, key, value),
                )
        else:
            file_id = row["id"]
            cursor.execute(
                "SELECT category, key, value FROM metadata WHERE file_id = ?", (file_id,)
            )
            existing = {(r["category"], r["key"]): r["value"] for r in cursor.fetchall()}
            changes: List[Dict[str, Any]] = []

            for field, new_value in flat_metadata.items():
                old_value = existing.get(field)
                if old_value is None:
                    changes.append(
                        {
                            "category": field[0],
                            "key": field[1],
                            "change_type": "added",
                            "old_value": None,
                            "new_value": new_value,
                        }
                    )
                elif old_value != new_value:
                    changes.append(
                        {
                            "category": field[0],
                            "key": field[1],
                            "change_type": "updated",
                            "old_value": old_value,
                            "new_value": new_value,
                        }
                    )

            for field, old_value in existing.items():
                if field not in flat_metadata:
                    changes.append(
                        {
                            "category": field[0],
                            "key": field[1],
                            "change_type": "removed",
                            "old_value": old_value,
                            "new_value": None,
                        }
                    )

            if changes or row["file_hash"] != file_hash_val:
                cursor.execute(
                    """
                    UPDATE files
                    SET file_hash = ?, file_size = ?, file_mtime = ?, file_type = ?, extracted_at = ?, last_updated = ?
                    WHERE id = ?
                """,
                    (file_hash_val, file_size, file_mtime, file_type, now, now, file_id),
                )
                cursor.execute("DELETE FROM metadata WHERE file_id = ?", (file_id,))
                for (category, key), value in flat_metadata.items():
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO metadata (file_id, category, key, value)
                        VALUES (?, ?, ?, ?)
                    """,
                        (file_id, category, key, value),
                    )
                if changes:
                    _record_changes(cursor, file_id, changes, now)
            else:
                cursor.execute(
                    "UPDATE files SET last_updated = ? WHERE id = ?", (now, file_id)
                )

        if perceptual_hashes and isinstance(perceptual_hashes, dict):
            has_any = any(perceptual_hashes.get(k) for k in ["phash", "dhash", "ahash", "whash", "blockhash"])
            if has_any:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO perceptual_hashes (file_id, phash, dhash, ahash, whash, blockhash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        file_id,
                        perceptual_hashes.get("phash"),
                        perceptual_hashes.get("dhash"),
                        perceptual_hashes.get("ahash"),
                        perceptual_hashes.get("whash"),
                        perceptual_hashes.get("blockhash"),
                    ),
                )

        if is_favorite:
            cursor.execute(
                """
                INSERT OR REPLACE INTO favorites (file_id, added_at)
                VALUES (?, ?)
            """,
                (file_id, now),
            )

        conn.commit()
        return int(file_id)
    except Exception as e:
        conn.rollback()
        return -1
    finally:
        conn.close()


def get_file_metadata(file_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve all metadata for a file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT file_path, file_hash, file_size, file_type, extracted_at, last_updated FROM files WHERE id = ?", (file_id,))
    file_row = cursor.fetchone()
    
    if not file_row:
        conn.close()
        return None
    
    result = dict(file_row)
    
    cursor.execute("SELECT category, key, value FROM metadata WHERE file_id = ?", (file_id,))
    metadata = {}
    for row in cursor.fetchall():
        cat = row["category"]
        if cat not in metadata:
            metadata[cat] = {}
        metadata[cat][row["key"]] = row["value"]
    
    result["metadata"] = metadata
    
    cursor.execute("SELECT * FROM perceptual_hashes WHERE file_id = ?", (file_id,))
    hash_row = cursor.fetchone()
    if hash_row:
        result["perceptual_hashes"] = dict(hash_row)
    
    cursor.execute("SELECT * FROM favorites WHERE file_id = ?", (file_id,))
    fav_row = cursor.fetchone()
    result["is_favorite"] = bool(fav_row)
    
    conn.close()
    
    return result


def search_metadata(
    conditions: Optional[Dict[str, Any]] = None,
    file_types: Optional[List[str]] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Search files by metadata conditions.
    
    Example conditions:
        {"camera_make": "Canon", "iso_speed_ratings": "100", "width": 1920}
        Query format: camera:Canon, size:>5MB, date:2024
    
    Args:
        conditions: Key-value pairs to match
        file_types: List of file extensions to include
        limit: Maximum results
        offset: Pagination offset
    
    Returns:
        List of matching files with metadata
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT f.id, f.file_path, f.file_hash, f.file_size, f.file_type, f.extracted_at
        FROM files f
    """
    
    joins = []
    params = []
    
    if conditions:
        for key, value in conditions.items():
            alias = f"m_{len(joins)}"
            if isinstance(value, str) and value.startswith((">", "<", ">=", "<=", "!=")):
                op = value[:2]
                val = value[2:]
                joins.append(f"""
                    JOIN metadata {alias} ON f.id = {alias}.file_id
                    AND {alias}.key = ? AND {alias}.value {op} ?
                """)
            else:
                joins.append(f"""
                    JOIN metadata {alias} ON f.id = {alias}.file_id
                    AND {alias}.key = ? AND {alias}.value = ?
                """)
            params.extend([key, str(value)])
    
    query += " ".join(joins)
    
    if file_types:
        placeholders = ", ".join(["?"] * len(file_types))
        query += f" WHERE f.file_type IN ({placeholders})"
        params.extend(file_types)
    
    query += " ORDER BY f.extracted_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    
    results = []
    for row in cursor.fetchall():
        file_data = dict(row)
        file_data["metadata"] = {}
        
        cursor.execute("SELECT category, key, value FROM metadata WHERE file_id = ?", (file_data["id"],))
        for m_row in cursor.fetchall():
            cat = m_row["category"]
            if cat not in file_data["metadata"]:
                file_data["metadata"][cat] = {}
            file_data["metadata"][cat][m_row["key"]] = m_row["value"]
        
        results.append(file_data)
    
    conn.close()
    return results


def get_file_id_by_path(file_path: str) -> Optional[int]:
    """Resolve a file_id from a file path."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM files WHERE file_path = ?", (os.path.abspath(file_path),))
    row = cursor.fetchone()
    conn.close()
    return row["id"] if row else None


def get_version_history(file_id: int, limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
    """Retrieve version history records for a file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT changed_at, change_type, category, key, old_value, new_value
        FROM version_history
        WHERE file_id = ?
        ORDER BY changed_at DESC
        LIMIT ? OFFSET ?
    """,
        (file_id, limit, offset),
    )
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def _parse_query_value(value: str) -> Any:
    value = value.strip().strip('"').strip("'")
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        pass
    if value.lower() in ("true", "yes"):
        return True
    if value.lower() in ("false", "no"):
        return False
    return value


def _expand_shortcut(query_part: str) -> str:
    def parse_size(size_str: str) -> int:
        size_str = size_str.upper().strip()
        multipliers = {"KB": 1024, "MB": 1024**2, "GB": 1024**3, "B": 1}
        for unit, mult in multipliers.items():
            if size_str.endswith(unit):
                return int(float(size_str[: -len(unit)]) * mult)
        return int(size_str)

    shortcuts = {
        "filename:": ("file.file_path", "LIKE"),
        "name:": ("file.file_path", "LIKE"),
        "path:": ("file.file_path", "LIKE"),
        "camera:": ("normalized.camera_make", "LIKE"),
        "make:": ("normalized.camera_make", "LIKE"),
        "model:": ("normalized.camera_model", "LIKE"),
        "lens:": ("normalized.lens_model", "LIKE"),
        "format:": ("image.format", "="),
        "type:": ("file.file_type", "="),
    }

    for shortcut, (field, default_op) in shortcuts.items():
        if query_part.lower().startswith(shortcut):
            value = query_part[len(shortcut) :].strip()
            if value.startswith((">", "<", "!", "=")):
                return f"{field}{value}"
            return f"{field} {default_op} {value}"

    if query_part.lower().startswith("size:"):
        rest = query_part[5:].strip()
        op = "="
        for check_op in [">=", "<=", ">", "<", "="]:
            if rest.startswith(check_op):
                op = check_op
                rest = rest[len(check_op) :]
                break
        size_bytes = parse_size(rest)
        return f"file.file_size{op}{size_bytes}"

    if query_part.lower().startswith("date:"):
        rest = query_part[5:].strip()
        op = "LIKE"
        for check_op in [">=", "<=", ">", "<", "="]:
            if rest.startswith(check_op):
                op = check_op
                rest = rest[len(check_op) :]
                break
        if op == "LIKE":
            return f"filesystem.created LIKE {rest}"
        return f"filesystem.created{op}{rest}"

    if query_part.lower().startswith("width:"):
        rest = query_part[6:].strip()
        return f"image.width{rest}" if rest and rest[0] in "><=" else f"image.width={rest}"

    if query_part.lower().startswith("height:"):
        rest = query_part[7:].strip()
        return f"image.height{rest}" if rest and rest[0] in "><=" else f"image.height={rest}"

    return query_part


def _parse_simple_query(query: str) -> List[tuple]:
    conditions = []
    parts = query.split(" AND ")
    for part in parts:
        part = part.strip()
        if not part:
            continue
        part = _expand_shortcut(part)
        for op in [">=", "<=", "!=", ">", "<", "=", " LIKE ", " CONTAINS "]:
            if op in part:
                field, value = part.split(op, 1)
                field = field.strip()
                value = value.strip()
                operator = op.strip()
                conditions.append((field, operator, _parse_query_value(value)))
                break
    return conditions


def search_metadata_query(query: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Search metadata using a simple query language."""
    conditions = _parse_simple_query(query)
    if not conditions:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = """
        SELECT DISTINCT f.id, f.file_path, f.file_hash, f.file_size, f.file_type, f.extracted_at, f.file_mtime
        FROM files f
    """
    joins: List[str] = []
    where: List[str] = []
    params: List[Any] = []

    for idx, (field, operator, value) in enumerate(conditions):
        if field.startswith("file."):
            column = field.split(".", 1)[1]
            if operator in ("LIKE", "CONTAINS"):
                where.append(f"LOWER(f.{column}) LIKE LOWER(?)")
                params.append(f"%{value}%")
            else:
                where.append(f"f.{column} {operator} ?")
                params.append(value)
            continue

        if "." in field:
            category, key = field.split(".", 1)
        else:
            category, key = "normalized", field

        alias = f"m{idx}"
        joins.append(
            f"JOIN metadata {alias} ON f.id = {alias}.file_id AND {alias}.category = ? AND {alias}.key = ?"
        )
        params.extend([category, key])

        if operator in ("LIKE", "CONTAINS"):
            where.append(f"LOWER({alias}.value) LIKE LOWER(?)")
            params.append(f"%{value}%")
        elif operator in (">", "<", ">=", "<="):
            where.append(f"CAST({alias}.value AS REAL) {operator} ?")
            params.append(value)
        elif operator == "!=":
            where.append(f"{alias}.value != ?")
            params.append(str(value))
        else:
            where.append(f"{alias}.value = ?")
            params.append(str(value))

    query_sql = base_query + " " + " ".join(joins)
    if where:
        query_sql += " WHERE " + " AND ".join(where)
    query_sql += " ORDER BY f.extracted_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query_sql, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        file_id = row["id"]
        file_data = get_file_metadata(file_id)
        if file_data:
            results.append(file_data)
    return results


def find_similar_images(
    phash: str,
    threshold: int = 5,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """Find visually similar images using perceptual hash comparison."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ph.file_id, ph.phash, f.file_path, f.file_size, f.file_type
        FROM perceptual_hashes ph
        JOIN files f ON ph.file_id = f.id
        WHERE ph.phash IS NOT NULL
        LIMIT ?
    """, (limit * 2,))
    
    from .perceptual_hashes import hex_to_hash
    
    target_hash = hex_to_hash(phash)
    if not target_hash:
        return []
    
    candidates = []
    for row in cursor.fetchall():
        if row["phash"] == phash:
            continue
        
        candidate_hash = hex_to_hash(row["phash"])
        if candidate_hash:
            distance = target_hash - candidate_hash
            if distance <= threshold:
                candidates.append({
                    "file_id": row["file_id"],
                    "file_path": row["file_path"],
                    "file_size": row["file_size"],
                    "file_type": row["file_type"],
                    "hamming_distance": distance
                })
    
    conn.close()
    
    return sorted(candidates, key=lambda x: x["hamming_distance"])[:limit]


def toggle_favorite(file_id: int, notes: Optional[str] = None, tags: Optional[List[str]] = None) -> bool:
    """Toggle favorite status for a file."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT file_id FROM favorites WHERE file_id = ?", (file_id,))
    exists = cursor.fetchone() is not None
    
    now = datetime.now().isoformat()
    
    if exists:
        cursor.execute("DELETE FROM favorites WHERE file_id = ?", (file_id,))
    else:
        cursor.execute("""
            INSERT INTO favorites (file_id, added_at, notes, tags)
            VALUES (?, ?, ?, ?)
        """, (file_id, now, notes, json.dumps(tags) if tags else None))
    
    conn.commit()
    conn.close()
    
    return not exists


def get_favorites(limit: int = 100) -> List[Dict[str, Any]]:
    """Get all favorite files."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT f.*, fav.added_at, fav.notes, fav.tags
        FROM files f
        JOIN favorites fav ON f.id = fav.file_id
        ORDER BY fav.added_at DESC
        LIMIT ?
    """, (limit,))
    
    results = []
    for row in cursor.fetchall():
        file_data = dict(row)
        file_data["tags"] = json.loads(file_data["tags"] or "[]")
        results.append(file_data)
    
    conn.close()
    return results


def delete_file(file_id: int) -> bool:
    """Delete a file and its metadata from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM files WHERE id = ?", (file_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def get_statistics() -> Dict[str, Any]:
    """Get database statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM files")
    stats["total_files"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM favorites")
    stats["total_favorites"] = cursor.fetchone()[0]
    
    cursor.execute("SELECT file_type, COUNT(*) FROM files GROUP BY file_type")
    stats["by_type"] = {row[0]: row[1] for row in cursor.fetchall()}
    
    cursor.execute("SELECT SUM(file_size) FROM files")
    stats["total_size_bytes"] = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(DISTINCT file_hash) FROM files")
    stats["unique_files"] = cursor.fetchone()[0]
    
    conn.close()
    
    return stats
