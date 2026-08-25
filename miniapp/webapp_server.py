# -*- coding: utf-8 -*-
"""Bot Factory Studio Mini App — static server (Railway-ready)."""
from __future__ import annotations

import os
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

ROOT = Path(__file__).resolve().parent / "webapp"
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")

app = FastAPI(title="Bot Factory Studio Mini App")


def safe_file(folder: str, name: str) -> Path:
    if not SAFE_NAME.match(name or ""):
        raise HTTPException(status_code=400, detail="invalid name")
    path = (ROOT / folder / name).resolve()
    base = (ROOT / folder).resolve()
    if not str(path).startswith(str(base)) or not path.is_file():
        raise HTTPException(status_code=404, detail="not found")
    return path


@app.get("/")
async def index():
    index_path = ROOT / "index.html"
    if not index_path.is_file():
        return JSONResponse({"error": "index missing"}, status_code=500)
    return FileResponse(index_path)


@app.get("/health")
async def health():
    return {"ok": True, "app": "bot-factory-studio"}


@app.get("/css/{name}")
async def css(name: str):
    return FileResponse(safe_file("css", name))


@app.get("/js/{name}")
async def js(name: str):
    return FileResponse(safe_file("js", name))


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
