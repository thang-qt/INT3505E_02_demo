from flask import Flask, jsonify, request, abort
from uuid import uuid4

app = Flask(__name__)
books = {}
loans = {}


def require_fields(payload, fields):
    missing = [field for field in fields if field not in payload]
    if missing:
        abort(400, description="Missing fields: " + ", ".join(missing))


def get_book_or_404(book_id):
    book = books.get(book_id)
    if not book:
        abort(404, description="Book not found")
    return book


def get_loan_or_404(loan_id):
    loan = loans.get(loan_id)
    if not loan:
        abort(404, description="Loan not found")
    return loan


@app.route("/books", methods=["GET"])
def list_books():
    return jsonify(list(books.values()))


@app.route("/books", methods=["POST"])
def create_book():
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book_id = str(uuid4())
    book = {"id": book_id, "title": payload["title"], "author": payload["author"]}
    books[book_id] = book
    return jsonify(book), 201


@app.route("/books/<book_id>", methods=["GET"])
def retrieve_book(book_id):
    return jsonify(get_book_or_404(book_id))


@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book = get_book_or_404(book_id)
    book.update({"title": payload["title"], "author": payload["author"]})
    return jsonify(book)


@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = get_book_or_404(book_id)
    books.pop(book_id)
    return "", 204


@app.route("/loans", methods=["GET"])
def list_loans():
    return jsonify(list(loans.values()))


@app.route("/loans", methods=["POST"])
def create_loan():
    payload = request.get_json(force=True)
    require_fields(payload, ["book_id", "borrower"])
    if payload["book_id"] not in books:
        abort(404, description="Book not found")
    loan_id = str(uuid4())
    loan = {"id": loan_id, "book_id": payload["book_id"], "borrower": payload["borrower"]}
    loans[loan_id] = loan
    return jsonify(loan), 201


@app.route("/loans/<loan_id>", methods=["GET"])
def retrieve_loan(loan_id):
    return jsonify(get_loan_or_404(loan_id))


@app.route("/loans/<loan_id>", methods=["PUT"])
def update_loan(loan_id):
    payload = request.get_json(force=True)
    require_fields(payload, ["book_id", "borrower"])
    if payload["book_id"] not in books:
        abort(404, description="Book not found")
    loan = get_loan_or_404(loan_id)
    loan.update({"book_id": payload["book_id"], "borrower": payload["borrower"]})
    return jsonify(loan)


@app.route("/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    get_loan_or_404(loan_id)
    loans.pop(loan_id)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
