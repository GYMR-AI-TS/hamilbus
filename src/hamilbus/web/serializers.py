from __future__ import annotations

from typing import Any
from itertools import groupby

from ..datamodels import Line, Stop


def stop_payload(stop: Stop) -> dict[str, Any]:
    return {
        "index": stop.index,
        "name": stop.name,
        "type": stop.type,
        "lat": stop.lat,
        "lon": stop.lon,
        "lines": [line.index for line in stop.lines],
        "parent_station_idx": stop.parent_station_idx,
    }


def line_payload(line: Line) -> dict[str, Any]:
    if line.shape:
        shape = [{"lat": lat, "lon": lon} for lat, lon in line.shape]
    elif line.stops:
        shape = [{"lat": stop.lat, "lon": stop.lon} for stop in line.stops]
    else:
        shape = []

    return {
        "index": line.index,
        "name": line.name,
        "long_name": line.long_name,
        "color": line.color or "#3388ff",
        "shape": shape,
    }

def graph_lines_payload(edges: list[tuple]) -> list[dict[str, Any]]:
    """Group edges by line and return one entry per line with multiple segments."""
    # Group by line index (fall back to line name if index missing)
    grouped: dict[Any, dict] = {}
    for stop1, stop2, data in edges:
        line = data.get("line")
        key = line.index if line else -1
        if key not in grouped:
            grouped[key] = {
                "index": key,
                "name": line.name if line else "Edge",
                "long_name": line.long_name if line else "",
                "color": (line.color if line and line.color else None) or "#3388ff",
                "segments": [],
            }
        grouped[key]["segments"].append([
            {"lat": stop1.lat, "lon": stop1.lon},
            {"lat": stop2.lat, "lon": stop2.lon},
        ])
    return list(grouped.values())
