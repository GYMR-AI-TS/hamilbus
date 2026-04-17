from __future__ import annotations

from typing import Any

from ..datamodels import Line, Stop


def stop_payload(stop: Stop) -> dict[str, Any]:
    return {
        "index": stop.index,
        "name": stop.name,
        "type": stop.type,
        "lat": stop.lat,
        "lon": stop.lon,
        "lines": stop.lines,
        "parent_station_idx": stop.parent_station_idx,
    }


def line_payload(line: Line) -> dict[str, Any]:
    if line.shape:
        shape = [{"lat": lat, "lon": lon} for lon, lat in line.shape]
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
