### graph_builder.py
### Builds a graph from the raw data

from pyproj import Transformer
from shapely.geometry import Point, LineString
from collections import defaultdict


class GraphBuilder():
    """"""
    def __init__(self):
        pass

    def project(self, lon, lat):
        '''Project (lon,lat) coordinates in meters'''
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
        return transformer.transform(lon, lat)

    def extract_lines_shapes(self, file):
        lines = []
        return lines

    def extract_stops(self, file):
        stops = []
        return stops

    def merge_stops_by_name(self, stops):
        """Merge stops sharing the same name using centroid coordinates."""
        grouped = defaultdict(list)
        for stop in stops:
            grouped[stop["name"]].append(stop)

        merged_stops = []
        for name, group in grouped.items():
            centroid_lon = sum(stop["lon"] for stop in group) / len(group)
            centroid_lat = sum(stop["lat"] for stop in group) / len(group)
            merged_stops.append(
                {
                    "name": name,
                    "lon": centroid_lon,
                    "lat": centroid_lat,
                }
            )

        return merged_stops

    def determine_belonging(self, stop, lines, threshold=50):
        stop_projected = Point(self.project(point))
        lines = [LineString([self.project(lon, lat) for lon, lat in lines])]

        for line in lines : 
            distance = stop_projected.distance(line)
            if distance < threshold:
                point = point ### TODO : point belongs to line

        return point


