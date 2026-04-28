### graph_builder.py
### Builds a graph from the raw data

from tqdm import tqdm
from collections import defaultdict, Counter
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


class GraphBuilder:
    """Class to handle the operations to build to a graph from Stop and Line objects lists"""

    def __init__(self, stops: list[Stop] | None, lines: list[Line] | None, trips_by_lines: dict[str, list[str]] | None, stops_by_trips: dict[str, list[str]] | None) -> None:
        if stops is None:
            raise ValueError("'stops' cannot be None; pass a list[Stop].")
        if lines is None:
            raise ValueError("'lines' cannot be None; pass a list[Line].")
        if not isinstance(stops, list) or any(not isinstance(x, Stop) for x in stops):
            raise TypeError("'stops' must be a list of Stop objects.")
        if not isinstance(lines, list) or any(not isinstance(x, Line) for x in lines):
            raise TypeError("'lines' must be a list of Line objects.")
        self.stops = stops
        self.lines = lines
        self.trips_by_lines = trips_by_lines
        self.stops_by_trips = stops_by_trips
        self.merged_stops = None

    def merge_stops(self) -> list[Stop]:
        """Merge stops that are parent stations/substations of each others"""
        grouped = defaultdict(list)
        for stop in self.stops:
            if stop.type == "parent_station":
                grouped[stop.id].append(stop)
            else :
                grouped[stop.parent_station_id].append(stop)

        merged_stops = []
        for _, group in tqdm(
            grouped.items(), desc=f"Merging parent stations and substations", unit=" group of stops"
        ):
            centroid_lat = sum(stop.lat for stop in group) / len(group)
            centroid_lon = sum(stop.lon for stop in group) / len(group)
            centroid_lines = []
            id, name = group[0].id, group[0].name
            for stop in group:
                centroid_lines += [
                    line for line in stop.lines if line not in centroid_lines
                ]
                if stop.type == "parent_station":
                    id, name = stop.id, stop.name
            centroid_stop = Stop(
                id=id,
                name=name,
                type="centroid",
                lat=centroid_lat,
                lon=centroid_lon,
                lines=centroid_lines,
            )
            merged_stops.append(centroid_stop)
        self.merged_stops = merged_stops
        return merged_stops

    def build_new_graph(self) -> BusNetworkGraph:
        graph = BusNetworkGraph()
        stops_by_idx = {stop.id: stop for stop in self.stops}
        merged_stops_by_name = {stop.: stop for stop in self.merged_stops}
        for line in tqdm(self.lines, desc="Treating a line", unit="line"):
            for trip in self.trips_by_lines.get(line.index, []):
                trip_stops = self.stops_by_trips.get(trip, [])
                for stop_idx_1, stop_idx_2 in zip(trip_stops, trip_stops[1:]):
                    # Dedupe stops : get the corresponding centroid by name
                    stop1 = stops_by_idx[stop_idx_1]
                    stop2 = stops_by_idx[stop_idx_2]
                    stop1 = merged_stops_by_name[stop1.name]
                    stop2 = merged_stops_by_name[stop2.name]
                    # Populate line.stops
                    line.stops.append(stop1)
                    line.stops.append(stop2)
                    # Add nodes and edge
                    graph.add_stop(stop1)
                    graph.add_stop(stop2)
                    if not graph.has_edge(stop1.id, stop2.index):
                        graph.add_edge(stop1, stop2, line)
        return graph