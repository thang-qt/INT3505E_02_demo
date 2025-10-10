from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class BookCreate:
    title: str
    author: str
    publisher: str
    publication_year: int
    quantity: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookCreate":
        required = ["title", "author", "publisher", "publication_year", "quantity"]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError("Missing required fields")
        title = str(data["title"]).strip()
        author = str(data["author"]).strip()
        publisher = str(data["publisher"]).strip()
        if not title or not author or not publisher:
            raise ValueError("Fields must not be empty")
        try:
            publication_year = int(data["publication_year"])
            quantity = int(data["quantity"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid numeric fields") from exc
        if publication_year <= 0:
            raise ValueError("Publication year must be positive")
        if quantity < 0:
            raise ValueError("Quantity must be non-negative")
        return cls(title=title, author=author, publisher=publisher, publication_year=publication_year, quantity=quantity)


@dataclass(frozen=True)
class BookUpdate:
    title: Optional[str]
    author: Optional[str]
    publisher: Optional[str]
    publication_year: Optional[int]
    quantity: Optional[int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BookUpdate":
        if not data:
            raise ValueError("No fields provided")
        title = cls._normalize_optional_text(data.get("title"))
        author = cls._normalize_optional_text(data.get("author"))
        publisher = cls._normalize_optional_text(data.get("publisher"))
        publication_year = cls._normalize_optional_int(data.get("publication_year"))
        if publication_year is not None and publication_year <= 0:
            raise ValueError("Publication year must be positive")
        quantity = cls._normalize_optional_int(data.get("quantity"))
        return cls(title=title, author=author, publisher=publisher, publication_year=publication_year, quantity=quantity)

    @staticmethod
    def _normalize_optional_text(value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        if not text:
            raise ValueError("Fields must not be empty")
        return text

    @staticmethod
    def _normalize_optional_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            number = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid numeric fields") from exc
        if number < 0:
            raise ValueError("Numeric fields must be non-negative")
        return number
