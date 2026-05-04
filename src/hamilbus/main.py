import json
import numpy as np
import argparse
from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network
from hamilbus.solvers.or_tools_solver import ORToolsSolver
from hamilbus.distance_matrix import compute_distance_matrix
from hamilbus.pipeline import serve, run_pipeline, run_solver
from hamilbus.config import Settings, load_settings

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hamilbus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # hamilbus run
    run_p = subparsers.add_parser("run")
    run_p.add_argument("--gtfs-folder", type=Path)
    run_p.add_argument("--config", type=Path)

    # hamilbus solve
    solve_p = subparsers.add_parser("solve")
    solve_p.add_argument("--matrix", type=str)
    solve_p.add_argument("--solver", nargs="+")  # accepts multiple values
    solve_p.add_argument("--config", type=Path)

    # hamilbus serve
    serve_p = subparsers.add_parser("serve")
    serve_p.add_argument("--graph", type=str)
    serve_p.add_argument("--gtfs-folder", type=Path)
    serve_p.add_argument("--solution", type=str, nargs="+")  # accepts multiple values
    serve_p.add_argument("--config", type=Path)

    return parser


def dispatch(command: str, settings: Settings) -> None:
    if command == "run":
        run_pipeline(settings)
        pass
    elif command == "solve":
        run_solver(settings)
        pass
    elif command == "serve":
        serve(settings)


def main():
    args = build_parser().parse_args()
    settings = load_settings(
        config_path=args.config,  # None if --config wasn't passed
        cli_overrides=vars(args)  # the full argparse namespace as a dict
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
