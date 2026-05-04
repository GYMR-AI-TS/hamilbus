import argparse
from pathlib import Path
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


if __name__ == "__main__":
    main()
