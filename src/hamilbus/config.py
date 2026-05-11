### config.py
### Defines and populates the Settings dataclass with config.toml and CLI arguments

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum


DEFAULT_CONFIG_PATH = Path("hamilbus.toml")


class ResultType(Enum):
    CYCLE = "cycle"
    PATH = "path"


@dataclass
class Settings:
    # --- defaults live here ---
    # Paths
    gtfs_folder: Path = Path("./data")
    graph: Path | None = None
    matrices: Path | None = Path("./results")
    solutions: list[Path] | None = None
    output_dir: Path = Path("./results")
    # Parameters
    # The first 4 are not implemented yet
    ignored_lines: list[str] = field(default_factory=list)
    distance_method: str = "geodesic"
    result_type: ResultType = ResultType.CYCLE
    # start : None = default, "all" = all, list = specific stops
    start: list[int] | str | None = None
    solver: list[str] = field(default_factory=lambda: ["or_tools"])
    time_limit: int = 60
    complete_graph: bool = False
    serve: bool = False
    # Saving actions
    # False = don't save, True = use default output_dir, Path = specific path
    save_matrices: bool | Path = False
    save_solutions: bool | Path = False

    @classmethod
    def load(cls, config_path: Path | None, cli_overrides: dict = {}) -> Settings:
        # Start from defaults
        s = cls()

        # Override with config file
        resolved_config = (
            config_path if config_path is not None else DEFAULT_CONFIG_PATH
        )
        if resolved_config.exists():
            with open(resolved_config, "rb") as f:
                toml_data = tomllib.load(f)
            _apply_toml(s, toml_data)

        # Override with CLI
        _apply_cli(s, cli_overrides)

        return s


def _apply_toml(s: Settings, data: dict) -> None:
    paths = data.get("paths", {})
    if "gtfs_folder" in paths:
        s.gtfs_folder = Path(paths["gtfs_folder"])
    if "graph" in paths:
        s.graph = Path(paths["graph"])
    if "matrices" in paths:
        s.matrices = Path(paths["matrices"])
    if "solutions" in paths:
        s.solutions = Path(paths["solutions"])
    if "output_dir" in paths:
        s.output_dir = Path(paths["output_dir"])

    data_section = data.get("data", {})
    if "ignored_lines" in data_section:
        s.ignored_lines = data_section["ignored_lines"]

    graph = data.get("graph", {})
    if "complete_graph" in graph:
        s.complete_graph = graph["complete_graph"]
    if "distance_method" in graph:
        s.distance_method = graph["distance_method"]

    solver = data.get("solver", {})
    if "solver" in solver:
        s.solver = solver["solver"]
    if "result_type" in solver:
        s.result_type = ResultType(solver["result_type"])
    if "start" in solver:
        s.start = _parse_start(solver["start"])
    if "time_limit" in solver:
        s.time_limit = solver["time_limit"]

    output = data.get("output", {})
    if "save_matrices" in output:
        val = output["save_matrices"]
        # str → Path, bool stays bool
        s.save_matrices = Path(val) if isinstance(val, str) else val
    if "save_solutions" in output:
        val = output["save_solutions"]
        s.save_solutions = Path(val) if isinstance(val, str) else val
    if "serve" in output:
        s.serve = output["serve"]


def _apply_cli(s: Settings, cli: dict) -> None:
    if cli.get("gtfs_folder") is not None:
        s.gtfs_folder = cli["gtfs_folder"]
    if cli.get("graph") is not None:
        s.graph = cli["graph"]
    if cli.get("matrices") is not None:
        s.matrices = cli["matrices"]
    if cli.get("solution") is not None:
        s.solutions = cli["solutions"]
    if cli.get("ignored_lines") is not None:
        s.ignored_lines = cli["ignored_lines"]
    if cli.get("distance_method") is not None:
        s.distance_method = cli["distance_method"]
    if cli.get("result_type") is not None:
        s.result_type = ResultType(cli["result_type"])
    if cli.get("start") is not None:
        s.start = _parse_start(cli["start"])
    if cli.get("solver") is not None:
        s.solver = cli["solver"]
    if cli.get("complete_graph"):  # store_true: False when absent, True when present
        s.complete_graph = True
    if cli.get("time_limit"):
        s.time_limit = cli["time_limit"]
    if cli.get("save_matrices") is not None:
        val = cli["save_matrices"]
        # "default" → True, Path → Path
        s.save_matrices = True if val == "default" else val
    if cli.get("save_solutions") is not None:
        val = cli["save_solutions"]
        s.save_solutions = True if val == "default" else val
    if cli.get("serve"):
        s.serve = True


def _parse_start(value: list[str] | str | None) -> list[int] | str | None:
    if value is None:
        return None
    if value == ["all"] or value == "all":
        return "all"
    return [int(v) for v in value]
