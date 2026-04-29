### graph_builder.py
### Builds a graph from the raw data

from tqdm import tqdm
from collections import defaultdict
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


class GraphBuilder:
    """Class to handle the operations to build to a graph from Stop and Line objects lists"""

    def __init__(
        self,
        stops: list[Stop] | None,
        lines: list[Line] | None,
        trips_by_lines: dict[str, list[str]] | None,
        stops_by_trips: dict[str, list[str]] | None,
    ) -> None:
        if stops is None:
            raise ValueError("'stops' cannot be None; pass a list[Stop].")
        if lines is None:
            raise ValueError("'lines' cannot be None; pass a list[Line].")
        if trips_by_lines is None:
            raise ValueError("'trips_by_lines' cannot be None; pass a dict[str, list[str]].")
        if stops_by_trips is None:
            raise ValueError("'stops_by_trips' cannot be None; pass a dict[str, list[str]].")
        if not isinstance(stops, list) or any(not isinstance(x, Stop) for x in stops):
            raise TypeError("'stops' must be a list of Stop objects.")
        if not isinstance(lines, list) or any(not isinstance(x, Line) for x in lines):
            raise TypeError("'lines' must be a list of Line objects.")
        self.stops = stops
        self.lines = lines
        self.trips_by_lines = trips_by_lines
        self.stops_by_trips = stops_by_trips
        self.merged_stops = None
        self.stop_id_to_centroid = {s.id: s for s in self.stops}

    def merge_stops(self) -> list[Stop]:
        """Merge stops that are parent stations/substations of each others"""
        grouped = defaultdict(list)
        for stop in self.stops:
            if stop.type == "parent_station":
                grouped[stop.id].append(stop)
            else:
                grouped[stop.parent_station_id].append(stop)

        merged_stops = []
        stop_id_to_centroid = {}
        for _, group in tqdm(
            grouped.items(),
            desc="Merging parent stations and substations",
            unit=" group of stops",
        ):
            centroid_lat = sum(stop.lat for stop in group) / len(group)
            centroid_lon = sum(stop.lon for stop in group) / len(group)
            id, name = group[0].id, group[0].name
            for stop in group:
                if stop.type == "parent_station":
                    id, name = stop.id, stop.name
            centroid_stop = Stop(
                id=id,
                name=name,
                type="centroid",
                lat=centroid_lat,
                lon=centroid_lon,
            )
            merged_stops.append(centroid_stop)
            for stop in group:
                stop_id_to_centroid[stop.id] = centroid_stop
        self.merged_stops = merged_stops
        self.stop_id_to_centroid = stop_id_to_centroid
        return merged_stops

    def build_graph(self) -> BusNetworkGraph:
        graph = BusNetworkGraph()
        for line in tqdm(self.lines, desc="Creating the graph", unit=" lines"):
            for trip_id in self.trips_by_lines.get(line.id, []):
                trip_stops = self.stops_by_trips.get(trip_id, [])
                for stop_id_1, stop_id_2 in zip(trip_stops, trip_stops[1:]):
                    # Dedupe stops : get the corresponding centroid by name
                    stop1 = self.stop_id_to_centroid[stop_id_1]
                    stop2 = self.stop_id_to_centroid[stop_id_2]
                    # Populate line.stops and stop.lines
                    if stop1 not in line.stops:
                        line.stops.append(stop1)
                    if stop2 not in line.stops:
                        line.stops.append(stop2)
                    if line not in stop1.lines:
                        stop1.lines.append(line)
                    if line not in stop2.lines:
                        stop2.lines.append(line)
                    # Add nodes and edge
                    graph.add_stop(stop1)
                    graph.add_stop(stop2)
                    if not graph.has_edge(stop1.id, stop2.id):
                        graph.add_edge(stop1, stop2, line)
        return graph
