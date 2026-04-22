### graph_builder.py
### Builds a graph from the raw data

import tqdm
from pyproj import Transformer
from collections import defaultdict
from shapely.geometry import Point, LineString
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


class GraphBuilder:
    """Class to handle the operations to build to a graph from Stop and Line objects lists"""

    def __init__(self, stops: list[Stop], lines: list[Line]):
        self.stops = stops
        self.lines = lines
        self.transformer = Transformer.from_crs(
            "EPSG:4326", "EPSG:2154", always_xy=True
        )
        self._line_geometries: dict[int, LineString] = {}
        self._line_bounds: dict[int, tuple[float, float, float, float]] = {}
        self._build_line_index()

    def _build_line_index(self) -> None:
        """Project line shapes once and cache their geometries/bounds."""
        for line in self.lines:
            shape_projected = [
                self.project(coords[0], coords[1]) for coords in line.shape
            ]
            linestring = LineString(shape_projected)
            self._line_geometries[line.index] = linestring
            self._line_bounds[line.index] = linestring.bounds

    def project(self, lon: float, lat: float):
        """Project (lon,lat) coordinates in meters"""
        # lon,lat instead of lat,lon by convention (always_xy=True)
        return self.transformer.transform(lon, lat)

    def determine_belonging(self, stop: Stop, line: Line, threshold=50) -> bool:
        """Determine if a stop belongs to a line by checking if it is close enough"""
        stop_projected = Point(self.project(stop.lon, stop.lat))
        line_bounds = self._line_bounds[line.index]
        minx, miny, maxx, maxy = line_bounds
        # Check if the stop belongs in the Line's bounding box + threshold
        if not (
            minx - threshold <= stop_projected.x <= maxx + threshold
            and miny - threshold <= stop_projected.y <= maxy + threshold
        ):
            return False
        # Only if it does, calculate its distance to the line to determine belonging
        linestring = self._line_geometries[line.index]
        distance = stop_projected.distance(linestring)
        if distance < threshold:
            # We populate stop.lines but line.stops will come after deduping stops
            if line.index not in stop.lines:
                stop.lines.append(line.index)
            return True
        else:
            return False

    def assign_stops_to_lines(self, threshold: float = 50) -> None:
        """Populate each stop with all nearby lines using cached geometries."""
        for stop in tqdm(self.stops, desc="Assigning stops to lines", unit="stop"):
            for line in self.lines:
                self.determine_belonging(stop, line, threshold=threshold)

    def merge_stops_by_name(self, stops: list[Stop] = None) -> list[Stop]:
        """Merge stops sharing the same name using centroid coordinates."""
        if stops is None:
            stops = self.stops
        grouped = defaultdict(list)
        for stop in stops:
            # grouped = {"stopName" : [all stops with that name], ...}
            grouped[stop.name].append(stop)
        merged_stops = []
        for name, group in grouped.items():
            centroid_lat = sum(stop.lat for stop in group) / len(group)
            centroid_lon = sum(stop.lon for stop in group) / len(group)
            centroid_lines = []
            for stop in group:
                centroid_lines += [
                    line for line in stop.lines if line not in centroid_lines
                ]
                if stop.type == "parent_station":
                    idx = stop.index
            centroid_stop = Stop(
                index=idx,
                name=name,
                type="centroid",
                lat=centroid_lat,
                lon=centroid_lon,
                lines=centroid_lines,
                parent_station_idx=None,
            )
            merged_stops.append(centroid_stop)
        return merged_stops

    def order_stops(self, stops: list[Stop] = None):
        """Populate line.stops with ordered stops for all lines associated to a stop"""
        if stops is None:
            stops = self.stops
        grouped = defaultdict(list)
        for stop in stops:
            for line in stop.lines:
                grouped[line].append(stop)  # {line : [list of stops], ...}

        for line, group in grouped.items():
            shape_projected = [
                self.project(coords[1], coords[0]) for coords in line.shape
            ]
            linestring = LineString(shape_projected)
            stop_positions = []
            # Project each stop onto the line and get its position along the route
            for stop in group:
                stop_projected = Point(self.project(stop.lon, stop.lat))
                position = linestring.project(stop_projected, normalized=True)
                stop_positions.append((position, stop))

            # Sort by position along the route → this is the stop order
            stop_positions.sort(key=lambda x: x[0])
            ordered_stops = [stop for _, stop in stop_positions]
            line.stops = ordered_stops

    def build_graph(self, lines: list[Line] = None) -> BusNetworkGraph:
        """Builds a BusNetworkGraph object from a list of Line objects with ordered stops"""
        if lines is None:
            lines = self.lines
        graph = BusNetworkGraph()
        for line in lines:
            graph.add_line(line)
        return graph
