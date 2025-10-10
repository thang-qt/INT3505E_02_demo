import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = Path(os.environ.get("LIBRARY_DB_PATH", BASE_DIR / "library.db"))
API_PREFIX = "/api"
DEFAULT_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get("LIBRARY_ALLOWED_ORIGINS", ",".join(DEFAULT_ALLOWED_ORIGINS)).split(",") if origin.strip()]
BOOK_CACHE_MAX_AGE = int(os.environ.get("LIBRARY_BOOK_CACHE_MAX_AGE", "60"))
OPENAPI_ROUTE = "/openapi.json"
SWAGGER_URL = "/docs"
