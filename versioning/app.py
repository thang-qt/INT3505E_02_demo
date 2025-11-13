from flask import Flask

from api_v1 import v1_bp
from api_v2 import v2_bp


def create_app() -> Flask:
    """Create a Flask app that exposes v1 and v2 payment APIs."""
    app = Flask(__name__)
    app.register_blueprint(v1_bp, url_prefix="/v1")
    app.register_blueprint(v2_bp, url_prefix="/v2")
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
