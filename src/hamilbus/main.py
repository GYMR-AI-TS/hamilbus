import argparse
from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network
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

    # hamilbus serve
    serve_p = subparsers.add_parser("serve")
    serve_p.add_argument("--solution", type=str)

    return parser


def dispatch(command: str, settings: Settings) -> None:
    if command == "run":
        #run_pipeline(settings)
        pass
    elif command == "solve":
        #run_solver(settings)
        pass
    elif command == "serve":
        #run_server(settings)
        pass


def main():
    args = build_parser().parse_args()
    settings = load_settings(
        config_path=args.config,  # None if --config wasn't passed
        cli_overrides=vars(args)  # the full argparse namespace as a dict
    )
    dispatch(args.command, settings)


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""

    DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
    stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(DATA_DIR)

    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    graph_builder.merge_stops()
    graph = graph_builder.build_graph()

    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
