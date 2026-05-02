### distance_matrix.py
### Computes the shortest distance between all pairs of nodes in the graph and stores the paths

import networkx as nx
from .datamodels import BusNetworkGraph
import numpy as np
from tqdm import tqdm


def compute_distance_matrix(
    bus_graph: BusNetworkGraph, strategy: str = "dijkstra"
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Computes the shortest distance and path between all pairs of stops in the graph."""

    stops_index_to_id = {
        idx: stop_id for idx, stop_id in enumerate(bus_graph.graph.nodes)
    }
    len_stops = len(bus_graph.graph.nodes)
    distance_matrix = np.zeros((len_stops, len_stops))
    path_matrix = np.empty((len_stops, len_stops), dtype=object)
    strategy_func = {
        "dijkstra": nx.single_source_dijkstra,
        "bellman-ford": nx.single_source_bellman_ford,
    }

    for u_idx in tqdm(range(len_stops), desc="Computing the distance matrix", unit=" stops"):
        for v_idx in range(len_stops):
            if u_idx != v_idx:
                try:
                    length, path = strategy_func[strategy](
                        bus_graph.graph,
                        stops_index_to_id[u_idx],
                        stops_index_to_id[v_idx],
                        weight="distance",
                    )
                    path_matrix[u_idx, v_idx] = path
                    distance_matrix[u_idx, v_idx] = length

                except nx.NetworkXNoPath:
                    path_matrix[u_idx, v_idx] = None
                    # No path exists
                    distance_matrix[u_idx, v_idx] = np.inf
                    # Infinite distance if no path exists

            else:
                distance_matrix[u_idx, v_idx] = 0
                # Distance from a node to itself is 0
                path_matrix[u_idx, v_idx] = [u_idx]
                # Path from a node to itself is just the node

    return distance_matrix, path_matrix, stops_index_to_id
