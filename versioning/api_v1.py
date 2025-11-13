from __future__ import annotations

from flask import Blueprint, jsonify, request

v1_bp = Blueprint("payments_v1", __name__)

_payments: list[dict[str, object]] = []
_next_id = 1


def _generate_id() -> int:
    global _next_id
    payment_id = _next_id
    _next_id += 1
    return payment_id


@v1_bp.get("/payment")
def list_payments():
    """Return every captured payment (very small, in-memory store)."""
    return jsonify(_payments)


@v1_bp.post("/payment")
def create_payment():
    """Create a payment capture with amount + currency, no validation extras."""
    payload = request.get_json(silent=True) or {}
    missing = {"amount", "currency"} - payload.keys()
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(sorted(missing))}"}), 400

    payment = {
        "id": f"pay_{_generate_id()}",
        "amount": payload["amount"],
        "currency": payload["currency"],
        "status": "captured",
    }
    _payments.append(payment)
    return jsonify(payment), 201


@v1_bp.get("/payment/<payment_id>")
def get_payment(payment_id: str):
    payment = next((p for p in _payments if p["id"] == payment_id), None)
    if not payment:
        return jsonify({"error": "payment not found"}), 404
    return jsonify(payment)
