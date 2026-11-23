"""Serve the Puribot UI and API together using Uvicorn."""

from pathlib import Path

from fastapi.staticfiles import StaticFiles

from api.index import app

public_dir = Path(__file__).resolve().parent / "public"
app.mount("/", StaticFiles(directory=public_dir, html=True), name="frontend")
