from typing import Any, Dict, List, Optional

from ..db import get_connection


def list_books() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, author, publisher, publication_year, quantity FROM books ORDER BY id"
        ).fetchall()
        return [dict(row) for row in rows]


def get_book(book_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, title, author, publisher, publication_year, quantity FROM books WHERE id = ?",
            (book_id,),
        ).fetchone()
        return dict(row) if row else None


def create_book(data: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO books (title, author, publisher, publication_year, quantity) VALUES (?, ?, ?, ?, ?)",
            (
                data["title"],
                data["author"],
                data["publisher"],
                data["publication_year"],
                data["quantity"],
            ),
        )
        new_id = cursor.lastrowid
    created = get_book(new_id)
    if created is None:
        raise RuntimeError("Failed to load created book")
    return created


def update_book(book_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not data:
        return get_book(book_id)
    columns = []
    values: List[Any] = []
    for key, value in data.items():
        columns.append(f"{key} = ?")
        values.append(value)
    values.append(book_id)
    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE books SET {', '.join(columns)} WHERE id = ?",
            tuple(values),
        )
        if cursor.rowcount == 0:
            return None
    return get_book(book_id)


def delete_book(book_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        return cursor.rowcount > 0
