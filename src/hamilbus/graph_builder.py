### graph_builder.py
### Builds a graph from the raw data

from pyproj import Transformer
from shapely.geometry import Point, LineString
from collections import defaultdict
from hamilbus.datamodels import Stop, Line

class GraphBuilder():
    """"""
    def __init__(self, stops:list[Stop], lines:list[Line]):
        self.stops = stops
        self.lines = lines

    def project(self, lon:float, lat:float):
        '''Project (lon,lat) coordinates in meters'''
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
        return transformer.transform(lon, lat) # lon,lat instead of lat,lon by convention (always_xy=True)

    def determine_belonging(self, stop:Stop, line:Line, threshold=50) -> bool:
        '''Determine if a stop belongs to a line by checking if it is close enough'''
        stop_projected = Point(self.project(stop.lon, stop.lat))
        shape_projected = [self.project(coords[1], coords[0]) for coords in line.shape]
        linestring = LineString(shape_projected)
        
        distance = stop_projected.distance(linestring)
        if distance < threshold:
            if line.index not in stop.lines : # We populate stop.lines but line.stops will come after deduping stops
                stop.lines.append(line.index)
            return True
        else : 
            return False


    def merge_stops_by_name(self, stops:dict[int,Stop]) -> dict[int,Stop]:
        """Merge stops sharing the same name using centroid coordinates."""
        grouped = defaultdict(list)
        for stop in stops:
            grouped[stop.name].append(stop) # {"stopName" : [all stops with that name], ...}
        merged_stops = {}
        for name, group in grouped.items():
            centroid_lat = sum(stop["lat"] for stop in group) / len(group)
            centroid_lon = sum(stop["lon"] for stop in group) / len(group)
            centroid_lines = []
            for stop in group:
                centroid_lines += [line for line in stop.lines if line not in centroid_lines]
                if stop.type == "parent_station":
                    idx = stop.index
            centroid_stop = Stop(
                index = idx,
                name = name,
                type = "centroid",
                lat = centroid_lat,
                lon = centroid_lon,
                lines = centroid_lines, 
                parent_station_idx = None
            )
            merged_stops[idx] = centroid_stop
        return merged_stops

    def order_stops(self, line):
        pass

    def build_graph(self, lines):
        pass


