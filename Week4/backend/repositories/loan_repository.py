from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..db import get_connection


def list_loans(include_history: bool) -> List[Dict[str, Any]]:
    query = "SELECT id, book_id, borrower, loaned_at, returned_at FROM loans"
    if not include_history:
        query += " WHERE returned_at IS NULL"
    query += " ORDER BY loaned_at DESC, id DESC"
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]


def get_loan(loan_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, book_id, borrower, loaned_at, returned_at FROM loans WHERE id = ?",
            (loan_id,),
        ).fetchone()
        return dict(row) if row else None


def create_loan(book_id: int, borrower: str) -> Optional[Dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE books SET quantity = quantity - 1 WHERE id = ? AND quantity > 0",
            (book_id,),
        )
        if cursor.rowcount == 0:
            return None
        cursor = conn.execute(
            "INSERT INTO loans (book_id, borrower, loaned_at) VALUES (?, ?, ?)",
            (book_id, borrower, timestamp),
        )
        loan_id = cursor.lastrowid
    return get_loan(loan_id)


def mark_returned(loan_id: int) -> Optional[Dict[str, Any]]:
    timestamp = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT book_id FROM loans WHERE id = ? AND returned_at IS NULL",
            (loan_id,),
        ).fetchone()
        if row is None:
            return None
        conn.execute(
            "UPDATE loans SET returned_at = ? WHERE id = ?",
            (timestamp, loan_id),
        )
        conn.execute(
            "UPDATE books SET quantity = quantity + 1 WHERE id = ?",
            (row["book_id"],),
        )
    return get_loan(loan_id)
