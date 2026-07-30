"""Application configuration."""

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_ROWS = 100_000
MAX_COLUMNS = 200
PREVIEW_ROWS = 12
MAX_CHART_POINTS = 2_000
ALLOWED_EXTENSIONS = {".csv"}

