import base64
import hashlib
import hmac
import json
import time
from flask import Flask, jsonify, request, abort
from uuid import uuid4

app = Flask(__name__)
books = {}
loans = {}
users = {"admin": {"password": "admin"}}
SECRET = "change-me"


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def encode_jwt(payload):
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = b64url_encode(json.dumps(header, separators=(",", ":")).encode())
    payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{header_b64}.{payload_b64}".encode()
    signature = hmac.new(SECRET.encode(), signing_input, hashlib.sha256).digest()
    signature_b64 = b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_jwt(token):
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
    except ValueError:
        abort(401, description="Invalid token")
    signing_input = f"{header_b64}.{payload_b64}".encode()
    expected_signature = hmac.new(SECRET.encode(), signing_input, hashlib.sha256).digest()
    provided_signature = b64url_decode(signature_b64)
    if not hmac.compare_digest(provided_signature, expected_signature):
        abort(401, description="Invalid token")
    payload = json.loads(b64url_decode(payload_b64))
    if "exp" in payload and time.time() > payload["exp"]:
        abort(401, description="Token expired")
    return payload


def require_fields(payload, fields):
    missing = [field for field in fields if field not in payload]
    if missing:
        abort(400, description="Missing fields: " + ", ".join(missing))


def authenticate_request():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        abort(401, description="Missing token")
    token = auth_header.split(" ", 1)[1]
    payload = decode_jwt(token)
    return payload.get("sub")


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


@app.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(force=True)
    require_fields(payload, ["username", "password"])
    record = users.get(payload["username"])
    if not record or record["password"] != payload["password"]:
        abort(401, description="Invalid credentials")
    token = encode_jwt({"sub": payload["username"], "exp": int(time.time()) + 3600})
    return jsonify({"token": token})


@app.route("/books", methods=["GET"])
def list_books():
    authenticate_request()
    return jsonify(list(books.values()))


@app.route("/books", methods=["POST"])
def create_book():
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book_id = str(uuid4())
    book = {"id": book_id, "title": payload["title"], "author": payload["author"]}
    books[book_id] = book
    return jsonify(book), 201


@app.route("/books/<book_id>", methods=["GET"])
def retrieve_book(book_id):
    authenticate_request()
    return jsonify(get_book_or_404(book_id))


@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book = get_book_or_404(book_id)
    book.update({"title": payload["title"], "author": payload["author"]})
    return jsonify(book)


@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    authenticate_request()
    get_book_or_404(book_id)
    books.pop(book_id)
    return "", 204


@app.route("/loans", methods=["GET"])
def list_loans():
    authenticate_request()
    return jsonify(list(loans.values()))


@app.route("/loans", methods=["POST"])
def create_loan():
    authenticate_request()
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
    authenticate_request()
    return jsonify(get_loan_or_404(loan_id))


@app.route("/loans/<loan_id>", methods=["PUT"])
def update_loan(loan_id):
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["book_id", "borrower"])
    if payload["book_id"] not in books:
        abort(404, description="Book not found")
    loan = get_loan_or_404(loan_id)
    loan.update({"book_id": payload["book_id"], "borrower": payload["borrower"]})
    return jsonify(loan)


@app.route("/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    authenticate_request()
    get_loan_or_404(loan_id)
    loans.pop(loan_id)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
