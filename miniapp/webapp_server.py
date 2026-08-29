# -*- coding: utf-8 -*-
"""Bot Factory Studio Mini App — static + build API."""
from __future__ import annotations

import os
import re
import sys
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, Response

ROOT = Path(__file__).resolve().parent / "webapp"
_HERE = Path(__file__).resolve().parent
_CANDIDATES = [
    _HERE.parent / "factory",           # monorepo: miniapp/../factory
    _HERE / "factory",                  # miniapp/factory
    Path.cwd() / "factory",
    Path.cwd().parent / "factory",
]
for _f in _CANDIDATES:
    if _f.is_dir() and (_f / "templates.py").is_file():
        if str(_f) not in sys.path:
            sys.path.insert(0, str(_f))
        break

SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]+$")
APP_VERSION = "v6-FORM-SEND"

app = FastAPI(title="Bot Factory Studio Mini App")
NO_CACHE = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


def safe_file(folder: str, name: str) -> Path:
    name = (name or "").split("?")[0].split("#")[0]
    if not SAFE_NAME.match(name):
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
    return FileResponse(index_path, headers=NO_CACHE, media_type="text/html; charset=utf-8")


@app.get("/health")
async def health():
    has_tpl = False
    n = 0
    try:
        import templates as T
        has_tpl = True
        n = len(getattr(T, "TEMPLATES", {}) or {})
    except Exception:
        pass
    return {
        "ok": True,
        "version": APP_VERSION,
        "templates_import": has_tpl,
        "template_count": n,
    }


@app.get("/css/{name}")
async def css(name: str):
    return FileResponse(safe_file("css", name), headers=NO_CACHE)


@app.get("/js/{name}")
async def js(name: str):
    return FileResponse(safe_file("js", name), headers=NO_CACHE, media_type="application/javascript")


@app.post("/api/build")
async def api_build(request: Request):
    """Fallback: build ZIP when sendData to bot fails or for download."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(400, "JSON نامعتبر")

    template = str(body.get("template") or "").strip()
    brand = str(body.get("brand") or body.get("brand_name") or "").strip()
    welcome = str(body.get("welcome") or body.get("welcome_text") or "").strip()
    admin = str(body.get("admin") or body.get("admin_id") or "").strip()
    detail = str(body.get("detail") or "").strip()

    if not template or not brand:
        raise HTTPException(400, "template و brand لازم است")
    if not admin.isdigit():
        raise HTTPException(400, "admin باید عدد باشد")

    try:
        import templates as T
    except Exception as e:
        raise HTTPException(500, f"templates در دسترس نیست: {e}")

    if template not in T.TEMPLATES:
        raise HTTPException(400, f"قالب ناشناخته: {template}")

    payload = {
        "template": template,
        "brand_name": brand,
        "brand": brand,
        "welcome_text": welcome or f"به {brand} خوش آمدید",
        "welcome": welcome or f"به {brand} خوش آمدید",
        "admin_id": int(admin),
        "detail": detail,
    }
    try:
        pkg = T.build_package(payload)
    except Exception as e:
        raise HTTPException(500, f"ساخت ناموفق: {e}")

    safe_brand = re.sub(r"[^\w\-]+", "_", brand)[:24] or "bot"
    fname = f"bot_{safe_brand}.zip"
    return Response(
        content=pkg,
        media_type="application/zip",
        headers={
            **NO_CACHE,
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-BF-Version": APP_VERSION,
        },
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
