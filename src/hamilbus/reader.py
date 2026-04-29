### reader.py
### Functions to read the raw data from txt files

import csv
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict
from hamilbus.datamodels import Stop, Line


def load_stops(path: str | Path) -> list[Stop]:
    """Load stops and returns them as a list of Stop objects"""
    stops = []
    with open(path, encoding="utf-8") as f:
        stops_file = csv.DictReader(f)
        for row in tqdm(stops_file, desc="Reading stops in stops.txt", unit=" stops"):
            stop = Stop(
                id=row["stop_id"],
                name=row["stop_name"],
                type="substation" if row.get("parent_station") else "parent_station",
                lat=float(row["stop_lat"]),
                lon=float(row["stop_lon"]),
                parent_station_id=row["parent_station"]
                if row.get("parent_station")
                else None,
            )
            stops.append(stop)
    return stops


def load_lines(routes_path: str | Path) -> list[Line]:
    """Load lines and returns them as a list of Line objects"""
    lines = []
    with open(routes_path, encoding="utf-8") as f:
        routes_file = csv.DictReader(f)
        for row in tqdm(routes_file, desc="Reading lines in routes.txt", unit=" lines"):
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
        for row in tqdm(trips_file, desc="Reading trips in trips.txt", unit=" rows"):
            trips_by_lines[row["route_id"]].append(row["trip_id"])
    return trips_by_lines


def load_trips_stops(stop_times_path: str | Path) -> dict[str, list[str]]:
    with open(stop_times_path, encoding="utf-8") as f:
        stop_times_file = csv.DictReader(f)
        stops_by_trips = defaultdict(list)
        for row in tqdm(
            stop_times_file, desc="Reading trips stops in stop_times.txt", unit=" trips"
        ):
            stops_by_trips[row["trip_id"]].append(row["stop_id"])
    return stops_by_trips
