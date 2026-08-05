"""
web.api.app — FastAPI Application Entry Point

OpenSource Clipping Studio — Web GUI Backend

Run with:
    uvicorn web.api.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routes import jobs, files, settings, repliz_publish

from fastapi import UploadFile, File, HTTPException
from pathlib import Path

COOKIES_DIR = Path(__file__).parent / "storage" / "cookies"
COOKIES_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/api/cookies")
async def upload_cookies(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")

    # Validasi: pastikan format Netscape cookies.txt
    if "Netscape HTTP Cookie File" not in text and "\tTRUE\t" not in text:
        raise HTTPException(400, "File bukan cookies.txt format Netscape yang valid")

    cookies_path = COOKIES_DIR / "cookies.txt"
    cookies_path.write_bytes(content)
    return {"status": "ok", "message": "Cookies berhasil diupload"}

@app.get("/api/cookies/status")
async def cookies_status():
    exists = (COOKIES_DIR / "cookies.txt").exists()
    return {"exists": exists}

@app.delete("/api/cookies")
async def delete_cookies():
    path = COOKIES_DIR / "cookies.txt"
    if path.exists():
        path.unlink()
    return {"status": "deleted"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    print("🚀 OpenSource Clipping Studio — Backend starting...")
    yield
    print("👋 Backend shutting down...")


app = FastAPI(
    title="OpenSource Clipping Studio",
    description="AI Auto-Clipper & Teaser Generator — Web GUI API",
    version="1.12.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "https://naufalrizqullah.github.io",
        "https://stella-desain.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(jobs.router)
app.include_router(files.router)
app.include_router(settings.router)
app.include_router(repliz_publish.router)


@app.get("/")
async def root():
    return {
        "name": "OpenSource Clipping Studio",
        "version": "1.13.0",
        "docs": "/docs",
        "health": "/api/health",
    }

import os
import signal
import asyncio

@app.post("/api/shutdown")
async def shutdown_server():
    """Trigger graceful shutdown of the FastAPI server."""
    # Send SIGINT to own process to trigger uvicorn graceful shutdown
    async def _shutdown():
        await asyncio.sleep(0.5)
        os.kill(os.getpid(), signal.SIGINT)
    
    asyncio.create_task(_shutdown())
    return {"status": "shutting down", "message": "Server is stopping..."}
