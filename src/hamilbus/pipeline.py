### pipeline.py
### Orchestrates operations

import json
import numpy as np
import networkx as nx
from pathlib import Path
from hamilbus.config import Settings
import hamilbus.reader as reader
from hamilbus.datamodels import Line
from hamilbus.distance_matrix import compute_distance_matrix
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network
from hamilbus.solvers.or_tools_solver import ORToolsSolver


def serve(settings: Settings):
    """Start the Hamilbus local web viewer on port 3000 to visualize the network.
    Works from the raw GTFS data or from a pre-computed graph.
    Optionally overlay saved solutions."""
    if settings.graph:
        # Load an already saved graph
        graph = nx.read_graphml(settings.graph)
    else:
        # Create the graph from the GTFS files
        stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(settings.gtfs_folder)
        graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
        graph_builder.merge_stops()
        graph = graph_builder.build_graph()
    if settings.solution:
        # Load already saved solutions and add them to the graph
        for num, solution_path in enumerate(settings.solution):
            with open(solution_path, encoding="utf-8") as f:
                solution = json.load(f)
            solution_line = Line(
                id=f"Solution_{num}",
                name=f"Solution {num}",
                long_name=f"Solution {num}",
                color="#0905FC",
                stops=[],  # TODO
            )
            graph.add_line(solution_line)
    # Run the server
    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


def run_solver(settings: Settings):
    pass


def run_pipeline(settings: Settings):
    pass
