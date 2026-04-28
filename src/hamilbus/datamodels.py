### datamodels.py
### Defines the dataclasses for storing stops and lines info

from typing import Optional, List
from dataclasses import dataclass, field
import networkx as nx
from math import sqrt


@dataclass
class Stop:
    id: str
    name: str
    type: str  # parent_station, substation, or centroid
    lat: float
    lon: float
    lines: list[Line] = field(default_factory=list)
    parent_station_idx: Optional[int] = None


@dataclass
class Line:
    id: str
    name: str
    long_name: str
    color: str
    stops: list[Stop] = field(default_factory=list)


@dataclass
class BusNetworkGraph:
    """Represents a graph composed of stops connected by edges."""

    graph: nx.MultiGraph = field(default_factory=nx.MultiGraph)

    def add_stop(self, stop: Stop):
        """Adds a stop to the graph."""
        self.graph.add_node(stop.index, stop=stop)

    def add_edge(self, stop1: Stop, stop2: Stop, line: Line):
        """Adds an edge between two stops, with the line as an attribute."""
        self.graph.add_edge(
            stop1.index,
            stop2.index,
            line=line,
            distance=sqrt((stop1.lat - stop2.lat) ** 2 + (stop1.lon - stop2.lon) ** 2),
        )

    def add_line(self, line: Line):
        """Adds a line to the graph and connects its stops."""
        for stop in line.stops:
            self.add_stop(stop)
        for i in range(len(line.stops) - 1):
            self.add_edge(line.stops[i], line.stops[i + 1], line)

    def get_stops(self) -> List[Stop]:
        """Returns a list of all stops in the graph."""
        return [data["stop"] for _, data in self.graph.nodes(data=True)]

    def get_edges(self) -> List[tuple[Stop, Stop, dict]]:
        """Returns a list of all edges in the graph, with their attributes."""
        return [
            (self.graph.nodes[u]["stop"], self.graph.nodes[v]["stop"], data)
            for u, v, data in self.graph.edges(data=True)
        ]

    def fully_connected_graph(self) -> nx.Graph:
        """Returns a fully connected graph where each edge weight is the shortest distance between stops."""
        fully_connected = nx.Graph()
        for stop in self.get_stops():
            fully_connected.add_node(stop.index, stop=stop)

        for u in fully_connected.nodes:
            for v in fully_connected.nodes:
                if u != v and not fully_connected.has_edge(u, v):
                    stop_u = self.graph.nodes[u]["stop"]
                    stop_v = self.graph.nodes[v]["stop"]
                    line = Line(
                        index=-1,
                        name="Direct Connection",
                        long_name="Direct Connection",
                        color="gray",
                    )
                    fully_connected.add_edge(stop_u.index, stop_v.index, line=line)

        return fully_connected
