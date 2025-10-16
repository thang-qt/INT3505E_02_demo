from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, jsonify, request

from ..config import AUTH_PASSWORD, AUTH_SECRET, AUTH_TOKEN_TTL_SECONDS, AUTH_USERNAME
from ..schemas import LoginRequest

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/tokens")
def create_token():
    payload = request.get_json(silent=True) or {}
    try:
        credentials = LoginRequest.from_dict(payload)
    except ValueError as error:
        response = jsonify({"message": str(error)})
        response.status_code = 400
        response.headers["Cache-Control"] = "no-store"
        return response
    if not AUTH_SECRET:
        response = jsonify({"message": "Server misconfiguration"})
        response.status_code = 500
        response.headers["Cache-Control"] = "no-store"
        return response
    if credentials.username != AUTH_USERNAME or credentials.password != AUTH_PASSWORD:
        response = jsonify({"message": "Unauthorized"})
        response.status_code = 401
        response.headers["WWW-Authenticate"] = "Bearer"
        response.headers["Cache-Control"] = "no-store"
        return response
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=AUTH_TOKEN_TTL_SECONDS)
    claims = {"sub": credentials.username, "exp": expires_at}
    token = jwt.encode(claims, AUTH_SECRET, algorithm="HS256")
    response = jsonify({"token": token, "expires_at": expires_at.isoformat()})
    response.status_code = 201
    response.headers["Cache-Control"] = "no-store"
    return response
