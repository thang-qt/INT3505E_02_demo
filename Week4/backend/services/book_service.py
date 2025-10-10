from dataclasses import asdict
from typing import Any, Dict, List, Optional

from ..repositories.book_repository import create_book as repo_create_book
from ..repositories.book_repository import delete_book as repo_delete_book
from ..repositories.book_repository import get_book as repo_get_book
from ..repositories.book_repository import list_books as repo_list_books
from ..repositories.book_repository import update_book as repo_update_book
from ..schemas import BookCreate, BookUpdate


def get_all_books() -> List[Dict[str, Any]]:
    return repo_list_books()


def get_book(book_id: int) -> Optional[Dict[str, Any]]:
    return repo_get_book(book_id)


def create_book(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = BookCreate.from_dict(payload)
    return repo_create_book(asdict(candidate))


def update_book(book_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    candidate = BookUpdate.from_dict(payload)
    data = {key: value for key, value in asdict(candidate).items() if value is not None}
    return repo_update_book(book_id, data)


def delete_book(book_id: int) -> bool:
    return repo_delete_book(book_id)
