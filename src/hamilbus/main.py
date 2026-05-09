import json
import numpy as np
import argparse
from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network
from hamilbus.solvers.or_tools_solver import ORToolsSolver
from hamilbus.distance_matrix import compute_distance_matrix
from hamilbus.pipeline import serve, run_solver, run_pipeline
from hamilbus.config import Settings


def build_parser() -> argparse.ArgumentParser:
    """Build the parser to parse CLI arguments for different configurations."""
    parser = argparse.ArgumentParser(prog="hamilbus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # hamilbus serve
    # Visualize the network, from a graph or the raw data
    # Optionally visualize pre-saved solutions
    # No computation other than creating the graph if needed
    serve_p = subparsers.add_parser("serve")
    serve_p.add_argument("--gtfs-folder", type=Path)
    serve_p.add_argument("--graph", type=Path)
    serve_p.add_argument("--solution", type=Path, nargs="+")  # accepts multiple values
    serve_p.add_argument("--config", type=Path)

    # hamilbus solve
    # Solve for the optimal path from a pre-computed distance matrix
    # Optionally compare multiple solvers
    # Optionally launch the server to visualize the solutions
    # No graph or distance matrix computation, only solving
    solve_p = subparsers.add_parser("solve")
    solve_p.add_argument("--matrix", type=Path)
    solve_p.add_argument("--solver", type=str, nargs="+")  # accepts multiple values
    solve_p.add_argument(
        "--result-type", type=str, choices=["cycle", "path"], default=None
    )
    solve_p.add_argument("--start", nargs="+", type=str)
    solve_p.add_argument("--complete-graph", action="store_true")
    solve_p.add_argument(
        "--save-solution", nargs="?", const="default", default=None, type=Path
    )
    solve_p.add_argument("--serve", action="store_true")
    solve_p.add_argument("--config", type=Path)

    # hamilbus run
    # Run the full pipeline, from raw data to solution
    run_p = subparsers.add_parser("run")
    run_p.add_argument("--gtfs-folder", type=Path)
    run_p.add_argument("--graph", type=Path)
    run_p.add_argument("--ignored-lines", nargs="+", type=str)
    run_p.add_argument("--distance-method", type=str)
    run_p.add_argument(
        "--save-matrix", nargs="?", const="default", default=None, type=Path
    )
    run_p.add_argument("--solver", nargs="+")  # accepts multiple values
    run_p.add_argument(
        "--result-type", type=str, choices=["cycle", "path"], default=None
    )
    run_p.add_argument("--start", nargs="+", type=str)
    run_p.add_argument("--complete-graph", action="store_true")
    run_p.add_argument(
        "--save-solution", nargs="?", const="default", default=None, type=Path
    )
    run_p.add_argument("--serve", action="store_true")
    run_p.add_argument("--config", type=Path)

    return parser


def dispatch(command: str, settings: Settings) -> None:
    """Dispatch the different commands to their pipeline"""
    if command == "serve":
        serve(settings)
    elif command == "solve":
        run_solver(settings)
    elif command == "run":
        run_pipeline(settings)


def main():
    args = build_parser().parse_args()
    settings = Settings.load(
        config_path=args.config,  # None if --config wasn't passed
        cli_overrides=vars(args),  # The full argparse namespace as a dict
    )
    dispatch(args.command, settings)


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""
    # Check if there's already a distance_matrix saved
    npy_path = Path.cwd() / "distance_matrix.npy"
    if npy_path.exists():
        distance_matrix = np.load(npy_path)
    else:
        # Load the raw data
        DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
        stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(DATA_DIR)
        # Build the graph
        graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
        graph_builder.merge_stops()
        graph = graph_builder.build_graph()
        # Compute the distance matrix
        distance_matrix, path_matrix, stop_index_to_id = compute_distance_matrix(graph)
        # Save the results
        np.save(Path.cwd() / "path_matrix.npy", path_matrix)
        np.save(Path.cwd() / "distance_matrix.npy", distance_matrix)
        with open(Path.cwd() / "stop_index_to_id.json", "w", encoding="utf-8") as f:
            json.dump({str(k): v for k, v in stop_index_to_id.items()}, f, indent=2)

    solver = ORToolsSolver(distance_matrix)
    solution = solver.solve(time_limit_seconds=120)
    # Save the solution
    with open(Path.cwd() / "solution.json", "w", encoding="utf-8") as f:
        json.dump(solution, f, indent=2)

    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
