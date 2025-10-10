from flask import Blueprint, jsonify

from ..docs import build_openapi_spec

spec_bp = Blueprint("spec", __name__)


@spec_bp.get("/openapi.json")
def openapi():
    return jsonify(build_openapi_spec())
