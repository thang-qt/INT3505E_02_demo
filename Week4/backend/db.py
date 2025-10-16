import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .config import DATABASE_PATH

INITIAL_BOOKS = [
    ("Số đỏ", "Vũ Trọng Phụng", "NXB Văn học", 1936, 5),
    ("Dế Mèn phiêu lưu ký", "Tô Hoài", "NXB Kim Đồng", 1941, 10),
    ("Tắt đèn", "Ngô Tất Tố", "NXB Văn học", 1937, 7),
    ("Lão Hạc", "Nam Cao", "NXB Hội Nhà văn", 1943, 3),
    ("Truyện Kiều", "Nguyễn Du", "NXB Văn học", 1820, 2),
]


def init_db() -> None:
    path = Path(DATABASE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publisher TEXT NOT NULL,
                publication_year INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                borrower TEXT NOT NULL,
                loaned_at TEXT NOT NULL,
                returned_at TEXT,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            )
            """
        )
        cursor = conn.execute("SELECT COUNT(1) FROM books")
        count = cursor.fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO books (title, author, publisher, publication_year, quantity) VALUES (?, ?, ?, ?, ?)",
                INITIAL_BOOKS,
            )


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(Path(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
