"""Shared filesystem paths for the web API."""
from pathlib import Path

COOKIES_DIR = Path(__file__).parent / "storage" / "cookies"
COOKIES_DIR.mkdir(parents=True, exist_ok=True)
