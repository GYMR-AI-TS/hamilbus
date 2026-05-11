import argparse
from pathlib import Path
from hamilbus.config import Settings
from hamilbus.pipeline import serve, run_solver, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Build the parser to parse CLI arguments for different configurations."""
    parser = argparse.ArgumentParser(prog="hamilbus")
    subparsers = parser.add_subparsers(dest="command", required=True)
    # hamilbus serve
    serve_p = subparsers.add_parser("serve")
    serve_p.add_argument("--gtfs-folder", type=Path)
    serve_p.add_argument("--graph", type=Path)
    serve_p.add_argument("--solutions", type=Path, nargs="+")  # accepts multiple values
    serve_p.add_argument("--config", type=Path)
    # hamilbus solve
    solve_p = subparsers.add_parser("solve")
    solve_p.add_argument("--matrices", type=Path)
    solve_p.add_argument("--solver", type=str, nargs="+")
    solve_p.add_argument(
        "--result-type", type=str, choices=["cycle", "path"], default=None
    )
    solve_p.add_argument("--start", nargs="+", type=str)
    solve_p.add_argument("--complete-graph", action="store_true")
    solve_p.add_argument("--time_limit", type=int)
    solve_p.add_argument(
        "--save-solutions", nargs="?", const="default", default=None, type=Path
    )
    solve_p.add_argument("--serve", action="store_true")
    solve_p.add_argument("--config", type=Path)
    # hamilbus run
    run_p = subparsers.add_parser("run")
    run_p.add_argument("--gtfs-folder", type=Path)
    run_p.add_argument("--graph", type=Path)
    run_p.add_argument("--ignored-lines", nargs="+", type=str)
    run_p.add_argument("--distance-method", type=str)
    run_p.add_argument(
        "--save-matrices", nargs="?", const="default", default=None, type=Path
    )
    run_p.add_argument("--solver", nargs="+")
    run_p.add_argument(
        "--result-type", type=str, choices=["cycle", "path"], default=None
    )
    run_p.add_argument("--start", nargs="+", type=str)
    run_p.add_argument("--complete-graph", action="store_true")
    run_p.add_argument("--time_limit", type=int)
    run_p.add_argument(
        "--save-solutions", nargs="?", const="default", default=None, type=Path
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


if __name__ == "__main__":
    main()
