### graph_builder.py
### Builds a graph from the raw data

from tqdm import tqdm
from pyproj import Transformer
from collections import defaultdict, Counter
from shapely.geometry import Point, LineString
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


class GraphBuilder:
    """Class to handle the operations to build to a graph from Stop and Line objects lists"""

    def __init__(self, stops: list[Stop] | None, lines: list[Line] | None):
        if stops is None:
            raise ValueError("'stops' cannot be None; pass a list[Stop].")
        if lines is None:
            raise ValueError("'lines' cannot be None; pass a list[Line].")
        if not isinstance(stops, list) or any(not isinstance(s, Stop) for s in stops):
            raise TypeError("'stops' must be a list of Stop objects.")
        if not isinstance(lines, list) or any(not isinstance(l, Line) for l in lines):
            raise TypeError("'lines' must be a list of Line objects.")
        self.stops = stops
        self.lines = lines
        self.transformer = Transformer.from_crs(
            "EPSG:4326", "EPSG:2154", always_xy=True
        )
        self._line_shapes: dict[int, LineString] = {}
        self._line_bounds: dict[int, tuple[float, float, float, float]] = {}
        self._build_lines()

    def _build_lines(self) -> None:
        """Project line shapes once and cache their linestrings/bounds."""
        for line in self.lines:
            shape_projected = [
                self.project(coords[0], coords[1]) for coords in line.shape
            ]
            linestring = LineString(shape_projected)
            self._line_shapes[line.index] = linestring
            self._line_bounds[line.index] = linestring.bounds

    def project(self, lon: float, lat: float):
        """Project (lon,lat) coordinates in meters"""
        # lon,lat instead of lat,lon by convention (always_xy=True)
        return self.transformer.transform(lon, lat)

    def determine_belonging(self, stop: Stop, line: Line, threshold: float=50) -> bool:
        """Determine if a stop belongs to a line by checking if it is close enough"""
        stop_projected = Point(self.project(stop.lon, stop.lat))
        line_bounds = self._line_bounds[line.index]
        min_x, min_y, max_x, max_y = line_bounds
        # Check if the stop belongs in the Line's bounding box + threshold
        if not (
            min_x - threshold <= stop_projected.x <= max_x + threshold
            and min_y - threshold <= stop_projected.y <= max_y + threshold
        ):
            return False
        # Only if it does, calculate its distance to the line to determine belonging
        distance = stop_projected.distance(self._line_shapes[line.index])
        if distance < threshold:
            # We populate stop.lines but line.stops will come after deduping stops
            if line.index not in stop.lines:
                stop.lines.append(line.index)
            return True
        else:
            return False

    def assign_stops_to_lines(self, threshold: float = 50) -> None:
        """Populate each stop with all nearby lines using cached shapes."""
        for stop in tqdm(self.stops, desc="Assigning stops to lines", unit="stop"):
            for line in self.lines:
                self.determine_belonging(stop, line, threshold=threshold)

    def merge_stops(self, strategy: str = "name") -> list[Stop]:
        """Merge stops using a chosen Stop attribute (defaults to name)."""
        grouped = defaultdict(list)
        for stop in self.stops:
            # grouped = {"stopName" : [all stops with that name], ...}
            if not hasattr(stop, strategy):
                raise ValueError(f"Invalid merge strategy '{strategy}' for Stop")
            grouped[getattr(stop, strategy)].append(stop)
        merged_stops = []
        for _, group in grouped.items():
            centroid_lat = sum(stop.lat for stop in group) / len(group)
            centroid_lon = sum(stop.lon for stop in group) / len(group)
            centroid_lines = []
            idx = group[0].index
            # Keep a human-readable stop name, even if merge strategy is not "name".
            centroid_name = Counter(stop.name for stop in group).most_common(1)[0][0]
            for stop in group:
                centroid_lines += [
                    line for line in stop.lines if line not in centroid_lines
                ]
                if stop.type == "parent_station":
                    idx = stop.index
            centroid_stop = Stop(
                index=idx,
                name=centroid_name,
                type="centroid",
                lat=centroid_lat,
                lon=centroid_lon,
                lines=centroid_lines,
                parent_station_idx=None,
            )
            merged_stops.append(centroid_stop)
        return merged_stops

    def order_stops(self):
        """Populate line.stops with ordered stops for all lines associated to a stop"""
        grouped = defaultdict(list)
        for stop in self.stops:
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

    def build_graph(self) -> BusNetworkGraph:
        """Builds a BusNetworkGraph object from a list of Line objects with ordered stops"""
        graph = BusNetworkGraph()
        for line in self.lines:
            graph.add_line(line)
        return graph
