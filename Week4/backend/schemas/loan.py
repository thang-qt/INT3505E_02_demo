from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class LoanCreate:
    book_id: int
    borrower: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoanCreate":
        if "book_id" not in data or "borrower" not in data:
            raise ValueError("Missing required fields")
        try:
            book_id = int(data["book_id"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Invalid book identifier") from exc
        if book_id <= 0:
            raise ValueError("Invalid book identifier")
        borrower = str(data["borrower"]).strip()
        if not borrower:
            raise ValueError("Borrower must not be empty")
        return cls(book_id=book_id, borrower=borrower)


@dataclass(frozen=True)
class LoanReturn:
    returned: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoanReturn":
        if "returned" not in data:
            raise ValueError("Missing required fields")
        returned = data["returned"]
        if returned is not True:
            raise ValueError("Return flag must be true")
        return cls(returned=True)
