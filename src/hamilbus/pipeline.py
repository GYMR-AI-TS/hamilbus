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
    # Validate it's a directory, not a file path
    if setting.suffix:
        raise ValueError(
            f"--save-solutions or --save-matrices expect a folder path, got '{setting}'. "
            f"Solutions are saved as solution_0.json, solution_1.json, etc."
            f"And matrices as distance_matrix.npy, path_matrix.npy and stops_index_to_id.json."
        )
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
        stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(
            settings.gtfs_folder
        )
        graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
        graph_builder.merge_stops()
        graph = graph_builder.build_graph()
    if settings.solutions:
        # Load already saved solutions and add them to the graph
        for num, solution_path in enumerate(settings.solutions):
            with open(solution_path, encoding="utf-8") as f:
                solution = json.load(f)
            solution_line = Line(
                id=f"Solution_{num}",
                name=f"Solution {num}",
                long_name=f"Solution {num}",
                color="#0905FC",
                stops=solution,  # TODO : not sure about saved solutions format ?
            )
            graph.add_line(solution_line)
    # Run the server
    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


solvers = {
    "or-tools": ORToolsSolver,
}


def run_solver(settings: Settings):
    """Runs one or more solvers on a pre-computed distance matrix. No graph or matrix computation.
    Optionally launch the server to visualize the solutions. Available options :
    --matrices, --solver, --result-type, --start, --complete-graph, --save-solutions, --serve"""
    try:
        distance_matrix = np.load(settings.matrices / "distance_matrix.npy")
        path_matrix = np.load(settings.matrices / "path_matrix.npy")
        with open(settings.matrices / "stops_index_to_id.json", encoding="utf-8") as f:
            stops_index_to_id = {float(k): v for k, v in json.load(f).items()}
    except Exception as e:
        print(e)
        return

    # TODO : handle different result_type and start
    solutions = []
    for solver_name in settings.solver:
        solver = solvers[solver_name](distance_matrix)
        s = solver.solve(time_limit_seconds=120)
        # TODO : add time_limit as a parameter of hamilbus solve and run
        solutions.append(s)

    if not settings.serve:
        # No graph needed
        reconstructor = PathReconstructor(stops_index_to_id, path_matrix)
        solutions = [reconstructor.format_solution(s, reconstruct=settings.complete_graph) for s in solutions]
    else:
        # Graph needed for display and solutions line creation
        if settings.graph:
            graph = nx.read_graphml(settings.graph)
        else:
            stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(
                settings.gtfs_folder
            )
            graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
            graph_builder.merge_stops()
            graph = graph_builder.build_graph()

        reconstructor = PathReconstructor(stops_index_to_id, graph, path_matrix)
        solutions = [reconstructor.format_solution(s, reconstruct=settings.complete_graph) for s in solutions]
        for s in solutions:
            reconstructor.add_solution_to_graph(s)

        set_graph_network(graph)
        run_server(host="127.0.0.1", port=3000)
        # TODO : add button to close the server (for below code to run)/save solutions from the server
    
    save_solutions_path = resolve_save_path(settings.save_solutions, settings.output_dir)
    if save_solutions_path:
        for num, solution in enumerate(solutions):
            with open(
                save_solutions_path / f"solution_{num}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(solution, f, indent=2)


def run_pipeline(settings: Settings):
    """Runs the full pipeline from raw GTFS data to solutions.
    Optionally launch the server to visualize the solutions. Available options :
    --gtfs-folder, --graph, --ignored-lines, --distance-method, --save-matrices,
    --solver, --result-type, --start, --complete-graph, --save-solutions, --serve"""
    if settings.graph:
        graph = nx.read_graphml(settings.graph)
    else:
        stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(
            settings.gtfs_folder
        )
        graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
        graph_builder.merge_stops()
        graph = graph_builder.build_graph()
    # TODO : handle ignored-lines
    # TODO : handle distance-method

    distance_matrix, path_matrix, stops_index_to_id = compute_distance_matrix(graph)
    save_matrix_path = resolve_save_path(settings.save_matrices, settings.output_dir)
    if save_matrix_path:
        np.save(save_matrix_path / "distance_matrix.npy", distance_matrix)
        np.save(save_matrix_path / "path_matrix.npy", path_matrix)
        with open(
            save_matrix_path / "stops_index_to_id.json", "w", encoding="utf-8"
        ) as f:
            json.dump({str(k): v for k, v in stops_index_to_id.items()}, f, indent=2)

    # TODO : handle different result_type and start
    solutions = []
    for solver_name in settings.solver:
        solver = solvers[solver_name](distance_matrix)
        s = solver.solve(time_limit_seconds=120)
        # TODO : add time_limit as a parameter
        solutions.append(s)

    reconstructor = PathReconstructor(stops_index_to_id, graph, path_matrix)
    solutions = [reconstructor.format_solution(s, reconstruct=settings.complete_graph) for s in solutions]
    if settings.serve:
        for s in solutions:
            reconstructor.add_solution_to_graph(s)
        set_graph_network(graph)
        run_server(host="127.0.0.1", port=3000)

    save_solutions_path = resolve_save_path(settings.save_solutions, settings.output_dir)
    if save_solutions_path:
        for num, solution in enumerate(solutions):
            with open(
                save_solutions_path / f"solution_{num}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(solution, f, indent=2)
