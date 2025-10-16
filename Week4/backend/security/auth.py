from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import jwt
from flask import Response, jsonify, request
from jwt import PyJWTError

from ..config import AUTH_SECRET

F = TypeVar("F", bound=Callable[..., Any])


def _token_from_header() -> str:
    header = request.headers.get("Authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:]
    return ""


def _decode_token(token: str) -> Optional[Dict[str, Any]]:
    if not token or not AUTH_SECRET:
        return None
    try:
        return jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except PyJWTError:
        return None


def _unauthorized_response() -> Response:
    response = jsonify({"message": "Unauthorized"})
    response.status_code = 401
    response.headers["WWW-Authenticate"] = "Bearer"
    response.headers["Cache-Control"] = "no-store"
    return response


def require_auth(func: F) -> F:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any):
        payload = _decode_token(_token_from_header())
        if payload is None:
            return _unauthorized_response()
        return func(*args, **kwargs)

    return cast(F, wrapper)
