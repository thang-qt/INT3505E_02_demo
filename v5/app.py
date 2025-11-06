import base64
import hashlib
import hmac
import json
import time
from flask import Flask, abort, request, url_for
from uuid import uuid4

app = Flask(__name__)
books = {
    "book-nguoi-la": {"id": "book-nguoi-la", "title": "Nguoi La Trong Guong", "author": "Nguyen Nhat Anh"},
    "book-dat-rung": {"id": "book-dat-rung", "title": "Dat Rung Phuong Nam", "author": "Doan Gioi"},
}
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

def json_response(data, status=200, cache_control="no-store", headers=None):
    body = json.dumps(data, separators=(",", ":"), sort_keys=True)
    response = app.response_class(body, status=status, mimetype="application/json")
    response.headers["Cache-Control"] = cache_control
    if headers:
        for key, value in headers.items():
            response.headers[key] = value
    return response

def cached_response(data, max_age=60):
    body = json.dumps(data, separators=(",", ":"), sort_keys=True)
    etag = hashlib.sha256(body.encode()).hexdigest()
    if request.headers.get("If-None-Match") == etag:
        response = app.response_class(status=304)
    else:
        response = app.response_class(body, mimetype="application/json")
    response.headers["Cache-Control"] = f"private, max-age={max_age}"
    response.headers["ETag"] = etag
    return response

def envelope(data, links=None, meta=None):
    payload = {"data": data}
    if links:
        payload["links"] = links
    if meta:
        payload["meta"] = meta
    return payload

def book_resource(book):
    return {
        "type": "book",
        "id": book["id"],
        "attributes": {
            "title": book["title"],
            "author": book["author"]
        },
        "links": {
            "self": url_for("retrieve_book", book_id=book["id"])
        }
    }

def loan_resource(loan):
    return {
        "type": "loan",
        "id": loan["id"],
        "attributes": {
            "borrower": loan["borrower"]
        },
        "relationships": {
            "book": {
                "data": {
                    "type": "book",
                    "id": loan["book_id"]
                },
                "links": {
                    "related": url_for("retrieve_book", book_id=loan["book_id"])
                }
            }
        },
        "links": {
            "self": url_for("retrieve_loan", loan_id=loan["id"])
        }
    }

@app.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(force=True)
    require_fields(payload, ["username", "password"])
    record = users.get(payload["username"])
    if not record or record["password"] != payload["password"]:
        abort(401, description="Invalid credentials")
    token = encode_jwt({"sub": payload["username"], "exp": int(time.time()) + 3600})
    return json_response(envelope({"token": token}, links={"self": url_for("login")}), cache_control="no-store")

@app.route("/books", methods=["GET"])
def list_books():
    authenticate_request()
    query_param = request.args.get("q", "")
    page_param = request.args.get("page", "1")
    size_param = request.args.get("page_size", "10")
    try:
        page = int(page_param)
        page_size = int(size_param)
    except ValueError:
        abort(400, description="Invalid pagination parameters")
    if page < 1 or page_size < 1 or page_size > 100:
        abort(400, description="Invalid pagination parameters")
    normalized_query = query_param.strip().lower()
    filtered_books = []
    for book in books.values():
        if not normalized_query or normalized_query in book["title"].lower() or normalized_query in book["author"].lower():
            filtered_books.append(book)
    total_items = len(filtered_books)
    if total_items == 0 and page != 1:
        abort(404, description="Page not found")
    total_pages = max(1, (total_items + page_size - 1) // page_size) if total_items else 1
    if total_items > 0 and page > total_pages:
        abort(404, description="Page not found")
    start = (page - 1) * page_size
    end = start + page_size
    paginated_books = filtered_books[start:end]
    resources = [book_resource(book) for book in paginated_books]
    meta = {
        "count": len(resources),
        "total_count": total_items,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
    if query_param:
        meta["query"] = query_param

    def page_link(target_page):
        params = {}
        if query_param:
            params["q"] = query_param
        params["page"] = target_page
        params["page_size"] = page_size
        return url_for("list_books", **params)
    links = {"self": page_link(page), "first": page_link(1), "last": page_link(total_pages)}
    if page > 1:
        links["prev"] = page_link(page - 1)
    if total_items > page * page_size:
        links["next"] = page_link(page + 1)
    return cached_response(envelope(resources, links=links, meta=meta))

@app.route("/books", methods=["POST"])
def create_book():
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book_id = str(uuid4())
    book = {"id": book_id, "title": payload["title"], "author": payload["author"]}
    books[book_id] = book
    resource = book_resource(book)
    location = resource["links"]["self"]
    return json_response(envelope(resource, links={"self": location}), status=201, headers={"Location": location})

@app.route("/books/<book_id>", methods=["GET"])
def retrieve_book(book_id):
    authenticate_request()
    book = books.get(book_id)
    if not book:
        abort(404, description="Book not found")
    resource = book_resource(book)
    return cached_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/books/<book_id>", methods=["PUT"])
def update_book(book_id):
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["title", "author"])
    book = books.get(book_id)
    if not book:
        abort(404, description="Book not found")
    book.update({"title": payload["title"], "author": payload["author"]})
    resource = book_resource(book)
    return json_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    authenticate_request()
    if book_id not in books:
        abort(404, description="Book not found")
    books.pop(book_id)
    response = app.response_class(status=204)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/loans", methods=["GET"])
def list_loans():
    authenticate_request()
    resources = [loan_resource(loan) for loan in loans.values()]
    meta = {"count": len(resources)}
    return cached_response(envelope(resources, links={"self": url_for("list_loans")}, meta=meta))

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
    resource = loan_resource(loan)
    location = resource["links"]["self"]
    return json_response(envelope(resource, links={"self": location}), status=201, headers={"Location": location})

@app.route("/loans/<loan_id>", methods=["GET"])
def retrieve_loan(loan_id):
    authenticate_request()
    loan = loans.get(loan_id)
    if not loan:
        abort(404, description="Loan not found")
    resource = loan_resource(loan)
    return cached_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/loans/<loan_id>", methods=["PUT"])
def update_loan(loan_id):
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["book_id", "borrower"])
    if payload["book_id"] not in books:
        abort(404, description="Book not found")
    loan = loans.get(loan_id)
    if not loan:
        abort(404, description="Loan not found")
    loan.update({"book_id": payload["book_id"], "borrower": payload["borrower"]})
    resource = loan_resource(loan)
    return json_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    authenticate_request()
    if loan_id not in loans:
        abort(404, description="Loan not found")
    loans.pop(loan_id)
    response = app.response_class(status=204)
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    app.run(debug=True)
