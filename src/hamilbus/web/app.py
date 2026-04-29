from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .serializers import line_payload, stop_payload, graph_lines_payload

_STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Hamilbus Local Viewer")
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")
_network: tuple | None = None  # (stops, lines)
_graph = None  # BusNetworkGraph


def set_network(stops, lines):
    global _network, _graph
    _network = (stops, lines)
    _graph = None


def set_graph(bus_network_graph):
    global _network, _graph
    _graph = bus_network_graph
    _network = None


@app.get("/api/stops")
def api_stops() -> JSONResponse:
    if _graph is not None:
        stops = _graph.get_stops()
    else:
        stops, _ = _network
    return JSONResponse([stop_payload(stop) for stop in stops])


@app.get("/api/lines")
def api_lines() -> JSONResponse:
    if _graph is not None:
        edges = _graph.get_edges()  # list[tuple[Stop, Stop, dict]]
        return JSONResponse(graph_lines_payload(edges))
    else:
        _, lines = _network
        return JSONResponse([line_payload(line) for line in lines])


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    html = (_STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html)
