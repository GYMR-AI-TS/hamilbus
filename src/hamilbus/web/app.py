from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from ..fake_network import _create_fake_network
from .serializers import line_payload, stop_payload

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Hamilbus Local Viewer")
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/api/stops")
def api_stops() -> JSONResponse:
    stops, _ = _create_fake_network()  # replace with real data loading
    return JSONResponse([stop_payload(stop) for stop in stops.values()])


@app.get("/api/lines")
def api_lines() -> JSONResponse:
    _, lines = _create_fake_network()  # replace with real data loading
    return JSONResponse([line_payload(line) for line in lines.values()])


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (_STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
