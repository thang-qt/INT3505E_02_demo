import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from urllib import error, request as urlrequest
from uuid import uuid4

from flask import Flask, abort, request, url_for

app = Flask(__name__)
books = {
    "book-nguoi-la": {"id": "book-nguoi-la", "title": "Nguoi La Trong Guong", "author": "Nguyen Nhat Anh"},
    "book-dat-rung": {"id": "book-dat-rung", "title": "Dat Rung Phuong Nam", "author": "Doan Gioi"},
}
loans = {}
users = {"admin": {"password": "admin"}}
webhook_subscriptions = {}
webhook_events = []
webhook_deliveries = []
SECRET = "change-me"
ALLOWED_WEBHOOK_EVENTS = {"loan.created", "loan.updated", "loan.deleted"}
WEBHOOK_HISTORY_LIMIT = 50

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

def webhook_subscription_resource(subscription):
    return {
        "type": "webhook-subscription",
        "id": subscription["id"],
        "attributes": {
            "url": subscription["url"],
            "events": subscription["events"],
            "secret": subscription["secret"],
            "created_at": subscription["created_at"],
        },
        "links": {"self": url_for("retrieve_webhook_subscription", subscription_id=subscription["id"])},
    }

def webhook_event_resource(event):
    return {"type": "webhook-event", "id": event["id"], "attributes": event}

def webhook_delivery_resource(delivery):
    return {"type": "webhook-delivery", "id": delivery["id"], "attributes": delivery}

def iso_timestamp():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def record_event(event_type, data):
    event = {"id": str(uuid4()), "type": event_type, "created_at": iso_timestamp(), "data": data}
    webhook_events.insert(0, event)
    del webhook_events[WEBHOOK_HISTORY_LIMIT:]
    return event

def sign_payload(secret, payload_bytes):
    return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

def dispatch_webhook(subscription, event):
    payload = json.dumps(event, separators=(",", ":"), sort_keys=True).encode()
    signature = sign_payload(subscription["secret"], payload)
    req = urlrequest.Request(
        subscription["url"],
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "LibraryAPI-Webhook/1.0",
            "X-Webhook-Event": event["type"],
            "X-Webhook-Signature": signature,
        },
        method="POST",
    )
    status_code = None
    success = False
    response_body = ""
    try:
        with urlrequest.urlopen(req, timeout=5) as resp:
            status_code = resp.status
            response_body = resp.read(256).decode(errors="ignore")
            success = 200 <= status_code < 300
    except error.HTTPError as exc:
        status_code = exc.code
        response_body = exc.read(256).decode(errors="ignore")
    except Exception as exc:
        response_body = str(exc)
    delivery = {
        "id": str(uuid4()),
        "subscription_id": subscription["id"],
        "event_id": event["id"],
        "attempted_at": iso_timestamp(),
        "status_code": status_code,
        "success": success,
        "response_sample": response_body,
    }
    webhook_deliveries.insert(0, delivery)
    del webhook_deliveries[WEBHOOK_HISTORY_LIMIT:]
    return success

def emit_event(event_type, data):
    event = record_event(event_type, data)
    for subscription in webhook_subscriptions.values():
        if event_type in subscription["events"]:
            dispatch_webhook(subscription, event)
    return event

def normalize_event_list(events):
    if events is None:
        return sorted(ALLOWED_WEBHOOK_EVENTS)
    if not isinstance(events, list) or not events:
        abort(400, description="Events must be a non-empty list")
    normalized = []
    for event_name in events:
        if event_name not in ALLOWED_WEBHOOK_EVENTS:
            abort(400, description=f"Unsupported event: {event_name}")
        if event_name not in normalized:
            normalized.append(event_name)
    return normalized

@app.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(force=True)
    require_fields(payload, ["username", "password"])
    record = users.get(payload["username"])
    if not record or record["password"] != payload["password"]:
        abort(401, description="Invalid credentials")
    token = encode_jwt({"sub": payload["username"], "exp": int(time.time()) + 3600})
    return json_response(envelope({"token": token}, links={"self": url_for("login")}), cache_control="no-store")

@app.route("/webhooks/subscriptions", methods=["GET"])
def list_webhook_subscriptions():
    authenticate_request()
    resources = [webhook_subscription_resource(sub) for sub in webhook_subscriptions.values()]
    meta = {"count": len(resources), "allowed_events": sorted(ALLOWED_WEBHOOK_EVENTS)}
    return json_response(envelope(resources, links={"self": url_for("list_webhook_subscriptions")}, meta=meta))

@app.route("/webhooks/subscriptions", methods=["POST"])
def create_webhook_subscription():
    authenticate_request()
    payload = request.get_json(force=True)
    require_fields(payload, ["url"])
    events = normalize_event_list(payload.get("events"))
    subscription_id = str(uuid4())
    secret = payload.get("secret") or uuid4().hex
    subscription = {
        "id": subscription_id,
        "url": payload["url"],
        "secret": secret,
        "events": events,
        "created_at": iso_timestamp(),
    }
    webhook_subscriptions[subscription_id] = subscription
    resource = webhook_subscription_resource(subscription)
    location = resource["links"]["self"]
    return json_response(envelope(resource, links={"self": location}), status=201, headers={"Location": location})

@app.route("/webhooks/subscriptions/<subscription_id>", methods=["GET"])
def retrieve_webhook_subscription(subscription_id):
    authenticate_request()
    subscription = webhook_subscriptions.get(subscription_id)
    if not subscription:
        abort(404, description="Subscription not found")
    resource = webhook_subscription_resource(subscription)
    return json_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/webhooks/subscriptions/<subscription_id>", methods=["DELETE"])
def delete_webhook_subscription(subscription_id):
    authenticate_request()
    if subscription_id not in webhook_subscriptions:
        abort(404, description="Subscription not found")
    webhook_subscriptions.pop(subscription_id)
    response = app.response_class(status=204)
    response.headers["Cache-Control"] = "no-store"
    return response

@app.route("/webhooks/events", methods=["GET"])
def list_webhook_events():
    authenticate_request()
    resources = [webhook_event_resource(event) for event in webhook_events]
    meta = {"count": len(resources)}
    return cached_response(envelope(resources, links={"self": url_for("list_webhook_events")}, meta=meta), max_age=5)

@app.route("/webhooks/deliveries", methods=["GET"])
def list_webhook_deliveries():
    authenticate_request()
    resources = [webhook_delivery_resource(delivery) for delivery in webhook_deliveries]
    meta = {"count": len(resources)}
    return cached_response(envelope(resources, links={"self": url_for("list_webhook_deliveries")}, meta=meta), max_age=5)

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
    emit_event("loan.created", {"loan": resource})
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
    emit_event("loan.updated", {"loan": resource})
    return json_response(envelope(resource, links={"self": resource["links"]["self"]}))

@app.route("/loans/<loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    authenticate_request()
    if loan_id not in loans:
        abort(404, description="Loan not found")
    loan = loans.pop(loan_id)
    resource = loan_resource(loan)
    emit_event("loan.deleted", {"loan": resource})
    response = app.response_class(status=204)
    response.headers["Cache-Control"] = "no-store"
    return response

if __name__ == "__main__":
    app.run(debug=True)
