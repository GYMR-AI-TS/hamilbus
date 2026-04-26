### distance_matrix.py
### Computes the shortest distance between all pairs of nodes in the graph and stores the paths

import networkx as nx
from .datamodels import BusNetworkGraph


def compute_distance_matrix(
    bus_graph: BusNetworkGraph, strategy: str = "dijkstra"
) -> dict:
    """Computes the shortest distance and path between all pairs of stops in the graph."""
    distance_matrix = {}
    strategy_func = {
        "dijkstra": nx.single_source_dijkstra,
        "bellman-ford": nx.single_source_bellman_ford,
    }

    for u in bus_graph.graph.nodes:
        for v in bus_graph.graph.nodes:
            if u != v:
                try:
                    length, path = strategy_func[strategy](
                        bus_graph.graph, u, v, weight="distance"
                    )
                    distance_matrix[(u, v)] = {"distance": length, "path": path}
                except nx.NetworkXNoPath:
                    distance_matrix[(u, v)] = {"distance": float("inf"), "path": []}
    return distance_matrix
