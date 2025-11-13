from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from flask import Blueprint, jsonify, request

v2_bp = Blueprint("payments_v2", __name__)

_payments_v2: dict[str, dict[str, object]] = {}


@v2_bp.get("/payment")
def list_payments_v2():
    """Return all payments with pagination metadata (static demo)."""
    items = list(_payments_v2.values())
    return jsonify({
        "items": items,
        "pagination": {"total": len(items), "has_more": False},
    })


@v2_bp.post("/payment")
def create_payment_v2():
    payload = request.get_json(silent=True) or {}
    missing = {"amount", "currency", "customer_id"} - payload.keys()
    if missing:
        return jsonify({"error": f"missing fields: {', '.join(sorted(missing))}"}), 400

    if not isinstance(payload["amount"], (int, float)) or payload["amount"] <= 0:
        return jsonify({"error": "amount must be a positive number"}), 400

    payment_id = f"pay_{uuid4().hex[:8]}"
    payment = {
        "id": payment_id,
        "amount": {
            "value": round(float(payload["amount"]), 2),
            "currency": payload["currency"],
        },
        "customer_id": payload["customer_id"],
        "capture_mode": payload.get("capture_mode", "automatic"),
        "status": "authorized" if payload.get("capture_mode") == "manual" else "captured",
        "fee": payload.get("fee", 0.0),
        "metadata": payload.get("metadata", {}),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _payments_v2[payment_id] = payment
    return jsonify(payment), 201


@v2_bp.patch("/payment/<payment_id>/capture")
def capture_payment(payment_id: str):
    payment = _payments_v2.get(payment_id)
    if not payment:
        return jsonify({"error": "payment not found"}), 404

    if payment["status"] == "captured":
        return jsonify(payment)

    payment["status"] = "captured"
    payment["captured_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(payment)


@v2_bp.delete("/payment/<payment_id>")
def cancel_payment(payment_id: str):
    payment = _payments_v2.get(payment_id)
    if not payment:
        return jsonify({"error": "payment not found"}), 404

    payment["status"] = "cancelled"
    payment["cancelled_at"] = datetime.now(timezone.utc).isoformat()
    return jsonify(payment)
