### reader.py
### Functions to read the raw data from txt files

import csv
from pathlib import Path
from hamilbus.datamodels import Stop, Line


def parse_stop_id(raw: str) -> int:
    """
    'FR_NAOLIB:StopPlace:194' -> 1_000_000 + 194 = 1000194
    'FR_NAOLIB:Quay:938'      -> 2_000_000 + 938 = 2000938
    """
    parts = raw.split(":")
    kind, num = parts[-2], int(parts[-1])
    if kind == "StopPlace":
        return 1_000_000 + num
    elif kind == "Quay":
        return 2_000_000 + num
    else:
        raise ValueError(f"Unknown stop kind: {kind} in {raw}")


def load_stops(path: str | Path) -> dict[int, Stop]:
    """Load stops and returns them as a dict of Stop objects by ids"""
    stops = {}
    with open(path, encoding="utf-8") as f:
        stops_file = csv.DictReader(f)
        for row in stops_file:
            stop = Stop(
                index = parse_stop_id(row["stop_id"]),
                name = row["stop_name"],
                type = "substation" if row.get("parent_station") else "parent_station",
                lat = float(row["stop_lat"]),
                lon = float(row["stop_lon"]),
                parent_station_idx = parse_stop_id(row["parent_station"]) if row.get("parent_station") else None,
            )
            stops[stop.index] = stop
    return stops


def parse_shape_line_name(raw: str) -> str:
    """
    'NAOLIBORG:JourneyPattern:C1_7EF3D0CF...' -> 'C1'
    """
    last_part = raw.split(":")[-1]                 # 'C1_7EF3D0CF...'
    return last_part.split("_", maxsplit=1)[0]     # 'C1'


def load_lines(routes_path: str | Path, shapes_path: str | Path) -> dict[int, Line]:
    """Load lines and returns them as a dict of Line objects by ids"""
    # First pass: read routes.txt
    lines = {}
    name_to_id = {}
    with open(routes_path, encoding="utf-8") as f:
        routes_file = csv.DictReader(f)
        for num, row in enumerate(routes_file):
            line = Line(
                index = num, 
                name = row["route_short_name"],
                long_name = row["route_long_name"],
                color = row["route_color"],
            )
            lines[line.index] = line
            name_to_id[line.name] = line.index

    # Second pass: read shapes.txt
    shape_rows: dict[int, list[tuple[int, float, float]]] = {}
    with open(shapes_path, encoding="utf-8") as f:
        shapes_file = csv.DictReader(f)
        for row in shapes_file:
            line_name = parse_shape_line_name(row["shape_id"])
            line_id = name_to_id[line_name]
            shape_rows.setdefault(line_id, []).append((
                int(row["shape_pt_sequence"]),
                float(row["shape_pt_lon"]),
                float(row["shape_pt_lat"]),
            ))

    for line_id, points in shape_rows.items():
        points.sort(key=lambda p: p[0])   # sort by sequence number
        if line_id in lines:
            lines[line_id].shape = [(lon, lat) for _, lon, lat in points]

    return lines