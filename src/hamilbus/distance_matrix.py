### distance_matrix.py
### Computes the shortest distance between all pairs of nodes in the graph and stores the paths

import networkx as nx
from .datamodels import BusNetworkGraph
import numpy as np

def compute_distance_matrix(
    bus_graph: BusNetworkGraph, strategy: str = "dijkstra"
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Computes the shortest distance and path between all pairs of stops in the graph."""

    stops_id_to_index = {stop_id: idx for idx, stop_id in enumerate(bus_graph.graph.nodes)}

    distance_matrix = np.zeros((len(bus_graph.graph.nodes), len(bus_graph.graph.nodes)))
    path_matrix = np.empty((len(bus_graph.graph.nodes), len(bus_graph.graph.nodes)), dtype=object)
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
                    path_matrix[stops_id_to_index[u], stops_id_to_index[v]] = path
                    distance_matrix[stops_id_to_index[u], stops_id_to_index[v]] = length

                except nx.NetworkXNoPath:
                    path_matrix[stops_id_to_index[u], stops_id_to_index[v]] = None  # No path exists
                    distance_matrix[stops_id_to_index[u], stops_id_to_index[v]] = np.inf  # Infinite distance if no path exists

            else:
                distance_matrix[stops_id_to_index[u], stops_id_to_index[v]] = 0  # Distance from a node to itself is 0
                path_matrix[stops_id_to_index[u], stops_id_to_index[v]] = [u]  # Path from a node to itself is just the node

    return path_matrix, distance_matrix, stops_id_to_index
