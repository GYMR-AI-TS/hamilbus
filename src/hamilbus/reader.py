### reader.py
### Functions to read the raw data from txt files

import csv
from pathlib import Path
from collections import defaultdict
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


def load_stops(path: str | Path) -> list[Stop]:
    """Load stops and returns them as a list of Stop objects"""
    stops = []
    with open(path, encoding="utf-8") as f:
        stops_file = csv.DictReader(f)
        for row in stops_file:
            stop = Stop(
                id=row["stop_id"],
                name=row["stop_name"],
                type="substation" if row.get("parent_station") else "parent_station",
                lat=float(row["stop_lat"]),
                lon=float(row["stop_lon"]),
                parent_station_idx=row["parent_station"] if row.get("parent_station") else None
            )
            stops.append(stop)
    return stops


def parse_shape_line_name(raw: str) -> str:
    """
    'NAOLIBORG:JourneyPattern:C1_7EF3D0CF...' -> 'C1'
    """
    last_part = raw.split(":")[-1]  # 'C1_7EF3D0CF...'
    return last_part.split("_", maxsplit=1)[0]  # 'C1'


def load_lines(routes_path: str | Path) -> list[Line]:
    """Load lines and returns them as a list of Line objects"""
    lines = []
    with open(routes_path, encoding="utf-8") as f:
        routes_file = csv.DictReader(f)
        for row in routes_file:
            line = Line(
                id=row["route_id"],
                name=row["route_short_name"],
                long_name=row["route_long_name"],
                color="#" + row["route_color"].upper(),
            )
            lines.append(line)
    return lines


def load_lines_trips(trips_path: str | Path) -> dict[str, list[str]]:
    with open(trips_path, encoding="utf-8") as f:
        trips_file = csv.DictReader(f)
        trips_by_lines = defaultdict(list)
        for row in trips_file:
            trips_by_lines[row["route_id"]].append(row["trip_id"])
    return trips_by_lines


def load_trips_stops(stop_times_path: str | Path):
    with open(stop_times_path, encoding="utf-8") as f:
        stop_times_file = csv.DictReader(f)
        stops_by_trips = defaultdict(list)
        for row in stop_times_file:
            stops_by_trips[row["trip_id"]].append(row["stop_id"])
    return stops_by_trips
