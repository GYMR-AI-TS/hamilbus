### pipeline.py
### Orchestrates operations

import json
import numpy as np
import networkx as nx
from pathlib import Path

from hamilbus.config import Settings
import hamilbus.reader as reader
from hamilbus.datamodels import Line
from hamilbus.path_reconstructor import PathReconstructor
from hamilbus.distance_matrix import compute_distance_matrix
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network
from hamilbus.solvers.or_tools_solver import ORToolsSolver


def resolve_save_path(setting: bool | Path, default_dir: Path) -> Path | None:
    if setting is False:
        return None
    if setting is True:
        return default_dir
    return setting


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
                stops=[],  # TODO : not sure about saved solution format ?
            )
            graph.add_line(solution_line)
    # Run the server
    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


solvers = {
    "or-tools":ORToolsSolver,
}

def run_solver(settings: Settings):
    """Runs one or more solvers on a pre-computed distance matrix. No graph or matrix computation. 
    Optionally launch the server to visualize the solutions. Available options :
    --matrix, --solver, --result-type, --start, --complete-graph, --save-solution, --serve"""
    distance_matrix = np.load(settings.matrix)
    stops_index_to_id = {}
    path_matrix = []
    # TODO : load path_matrix and stops_index_to_id as well

    # TODO : handle different result_type and start
    solutions = []
    for solver_name in settings.solver:
        solver = solvers[solver_name](distance_matrix)
        solution = solver.solve(time_limit_seconds=120)
        # TODO : add time_limit as a parameter
        solutions.append(solution)
    
    if not settings.serve:
        # No graph needed
        if settings.complete_graph:
            reconstructor = PathReconstructor(stops_index_to_id)
            solutions = [reconstructor.convert_indices_to_ids(solution) for solution in solutions]
        else :
            reconstructor = PathReconstructor(stops_index_to_id, path_matrix)
            solutions = [reconstructor.reconstruct_sparse_path(solution) for solution in solutions]
            # TODO : add an entry point to these two reconstructor functions with reconstruct=True/False directly ?
    else: 
        # Graph needed for display and solution line creation
        if settings.graph:
            graph = nx.read_graphml("graph.graphml")
        else:
            stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(settings.gtfs_folder)
            graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
            graph_builder.merge_stops()
            graph = graph_builder.build_graph()

        if settings.complete_graph:
            reconstructor = PathReconstructor(stops_index_to_id, graph)
            solutions = [reconstructor.convert_indices_to_ids(solution) for solution in solutions]
            for solution in solutions:
                reconstructor.add_solution_to_graph(solution, reconstruct=False)
        else :
            reconstructor = PathReconstructor(stops_index_to_id, graph, path_matrix)
            solutions = [reconstructor.reconstruct_sparse_path(solution) for solution in solutions]
            for solution in solutions:
                reconstructor.add_solution_to_graph(solution, reconstruct=True)
    
        set_graph_network(graph)
        run_server(host="127.0.0.1", port=3000)
    
    # TODO : add button to close the server (for below code to run)/save solutions from the server
    save_solution_path = resolve_save_path(settings.save_solution, settings.output_dir)
    # this works if a folder path was passed
    # TODO : handle case where a full path is passed : ./custom_folder/solution.json
    if save_solution_path:
        for num, solution in enumerate(solutions):
            with open(save_solution_path / f"solution_{num}.json", "w", encoding="utf-8") as f:
                json.dump(solution, f, indent=2)


def run_pipeline(settings: Settings):
    pass
