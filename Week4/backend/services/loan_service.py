from typing import Any, Dict, List, Optional

from ..repositories.book_repository import get_book as repo_get_book
from ..repositories.loan_repository import create_loan as repo_create_loan
from ..repositories.loan_repository import get_loan as repo_get_loan
from ..repositories.loan_repository import list_loans as repo_list_loans
from ..repositories.loan_repository import mark_returned as repo_mark_returned
from ..schemas import LoanCreate, LoanReturn


def _format_loan(record: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(record)
    payload["returned"] = payload.get("returned_at") is not None
    return payload


def get_all_loans(include_history: bool) -> List[Dict[str, Any]]:
    records = repo_list_loans(include_history)
    return [_format_loan(item) for item in records]


def get_loan(loan_id: int) -> Optional[Dict[str, Any]]:
    record = repo_get_loan(loan_id)
    if record is None:
        return None
    return _format_loan(record)


def create_loan(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = LoanCreate.from_dict(payload)
    book = repo_get_book(candidate.book_id)
    if book is None:
        raise LookupError("Book not found")
    if book["quantity"] <= 0:
        raise ValueError("Book is not available")
    record = repo_create_loan(candidate.book_id, candidate.borrower)
    if record is None:
        raise ValueError("Book is not available")
    return _format_loan(record)


def return_loan(loan_id: int, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    LoanReturn.from_dict(payload)
    record = repo_get_loan(loan_id)
    if record is None:
        return None
    if record.get("returned_at") is not None:
        raise ValueError("Loan already returned")
    updated = repo_mark_returned(loan_id)
    if updated is None:
        raise ValueError("Unable to return loan")
    return _format_loan(updated)
