from flask import Blueprint, jsonify, request

from ..config import BOOK_CACHE_MAX_AGE
from ..security.auth import require_auth
from ..services.book_service import create_book, delete_book, get_all_books, get_book, update_book

books_bp = Blueprint("books", __name__)


@books_bp.get("/books")
def list_books():
    books = get_all_books()
    response = jsonify(books)
    response.headers["Cache-Control"] = f"public, max-age={BOOK_CACHE_MAX_AGE}"
    return response


@books_bp.get("/books/<int:book_id>")
def retrieve_book(book_id: int):
    book = get_book(book_id)
    if book is None:
        return jsonify({"message": "Book not found"}), 404
    response = jsonify(book)
    response.headers["Cache-Control"] = f"public, max-age={BOOK_CACHE_MAX_AGE}"
    return response


@books_bp.post("/books")
@require_auth
def create_book_handler():
    payload = request.get_json(silent=True) or {}
    try:
        created = create_book(payload)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
    response = jsonify(created)
    response.status_code = 201
    response.headers["Cache-Control"] = "no-store"
    return response


@books_bp.put("/books/<int:book_id>")
@require_auth
def update_book_handler(book_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        updated = update_book(book_id, payload)
    except ValueError as error:
        return jsonify({"message": str(error)}), 400
    if updated is None:
        return jsonify({"message": "Book not found"}), 404
    response = jsonify(updated)
    response.headers["Cache-Control"] = "no-store"
    return response


@books_bp.delete("/books/<int:book_id>")
@require_auth
def delete_book_handler(book_id: int):
    deleted = delete_book(book_id)
    if not deleted:
        return jsonify({"message": "Book not found"}), 404
    response = jsonify({"message": "Book deleted"})
    response.status_code = 200
    response.headers["Cache-Control"] = "no-store"
    return response
