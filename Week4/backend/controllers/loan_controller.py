from flask import Blueprint, jsonify, request

from ..security.auth import require_auth
from ..services.loan_service import create_loan, get_all_loans, get_loan, return_loan

loans_bp = Blueprint("loans", __name__)


@loans_bp.get("/loans")
def list_loans():
    include_history = request.args.get("include_history", "false").lower() == "true"
    loans = get_all_loans(include_history)
    response = jsonify(loans)
    response.headers["Cache-Control"] = "no-store"
    return response


@loans_bp.get("/loans/<int:loan_id>")
def retrieve_loan(loan_id: int):
    loan = get_loan(loan_id)
    if loan is None:
        return jsonify({"message": "Loan not found"}), 404
    response = jsonify(loan)
    response.headers["Cache-Control"] = "no-store"
    return response


@loans_bp.post("/loans")
@require_auth
def create_loan_handler():
    payload = request.get_json(silent=True) or {}
    try:
        loan = create_loan(payload)
    except LookupError as error:
        return jsonify({"message": str(error)}), 404
    except ValueError as error:
        status = 409 if str(error) == "Book is not available" else 400
        return jsonify({"message": str(error)}), status
    response = jsonify(loan)
    response.status_code = 201
    response.headers["Cache-Control"] = "no-store"
    return response


@loans_bp.patch("/loans/<int:loan_id>")
@require_auth
def return_loan_handler(loan_id: int):
    payload = request.get_json(silent=True) or {}
    try:
        loan = return_loan(loan_id, payload)
    except ValueError as error:
        status = 409 if str(error) == "Loan already returned" else 400
        return jsonify({"message": str(error)}), status
    if loan is None:
        return jsonify({"message": "Loan not found"}), 404
    response = jsonify(loan)
    response.headers["Cache-Control"] = "no-store"
    return response
