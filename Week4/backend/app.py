import sys
from pathlib import Path
from typing import Optional

if __package__ in (None, ""):
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from backend.config import ALLOWED_ORIGINS, API_PREFIX, OPENAPI_ROUTE, SWAGGER_URL
    from backend.controllers.auth_controller import auth_bp
    from backend.controllers.book_controller import books_bp
    from backend.controllers.docs_controller import spec_bp
    from backend.controllers.loan_controller import loans_bp
    from backend.db import init_db
else:
    from .config import ALLOWED_ORIGINS, API_PREFIX, OPENAPI_ROUTE, SWAGGER_URL
    from .controllers.auth_controller import auth_bp
    from .controllers.book_controller import books_bp
    from .controllers.docs_controller import spec_bp
    from .controllers.loan_controller import loans_bp
    from .db import init_db

from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    init_db()
    app.register_blueprint(auth_bp, url_prefix=API_PREFIX)
    app.register_blueprint(books_bp, url_prefix=API_PREFIX)
    app.register_blueprint(loans_bp, url_prefix=API_PREFIX)
    app.register_blueprint(spec_bp)

    swagger_bp = get_swaggerui_blueprint(SWAGGER_URL, OPENAPI_ROUTE, config={"app_name": "Library API"})
    app.register_blueprint(swagger_bp, url_prefix=SWAGGER_URL)

    @app.get("/ping")
    def ping():
        return jsonify({"status": "ok"})

    @app.after_request
    def apply_cors(response):
        origin = request.headers.get("Origin")
        allowed_origin: Optional[str] = None
        if origin and origin in ALLOWED_ORIGINS:
            allowed_origin = origin
        elif not origin and ALLOWED_ORIGINS:
            allowed_origin = ALLOWED_ORIGINS[0]
        if allowed_origin:
            response.headers["Access-Control-Allow-Origin"] = allowed_origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "false"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,PATCH,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({"message": "Library API"})

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="0.0.0.0", port=5000)
