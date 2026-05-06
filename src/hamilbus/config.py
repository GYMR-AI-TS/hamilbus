### config.py
### 

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

class ResultType(Enum):
    CYCLE = "cycle"
    PATH = "path"

@dataclass
class Settings:
    # --- defaults live here ---
    # Paths
    gtfs_folder: Path = Path("./data")
    graph: Path | None = None
    matrix: Path | None = None
    solution: Path | None = None
    output_dir: Path = Path("./results")
    # Parameters
    ignored_lines: list[str] = field(default_factory=list)
    distance_method: str = "geodesic"
    result_type: ResultType = ResultType.CYCLE
    start: list[int] | str | None = None  # None = default, "all" = all, list = specific stops
    solver: list[str] = field(default_factory=lambda: ["or_tools"])
    complete_graph: bool = False
    serve: bool = False
    # Saving actions
    save_matrix: Path | str | None = None  # None = don't save, "default" = use output_dir, Path = specific path
    save_solution: Path | str | None = None


def load_settings(config_path: Path | None ="default path", cli_overrides: dict = {}) -> Settings:
    s = Settings()  # 1. start from defaults

    if config_path and config_path.exists():
        with open(config_path, "rb") as f:
            toml_data = tomllib.load(f)  # 2. override with config file
        _apply_toml(s, toml_data)

    _apply_cli(s, cli_overrides)  # 3. override with CLI

    return s


def _apply_toml(s: Settings, data: dict) -> None:
    paths = data.get("paths", {})
    if "gtfs_folder" in paths:
        s.gtfs_folder = Path(paths["gtfs_folder"])
    if "graph" in paths:
        s.graph = Path(paths["graph"])
    if "matrix" in paths:
        s.matrix = Path(paths["matrix"])
    if "solution" in paths:
        s.solution = Path(paths["solution"])
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

    output = data.get("output", {})
    if "output_dir" in output:
        s.output_dir = Path(output["output_dir"])
    if "save_matrix" in output:
        val = output["save_matrix"]
        if val is False:
            s.save_matrix = None
        elif val is True:
            s.save_matrix = "default"
        else:
            s.save_matrix = Path(val)
    if "save_solution" in output:
        val = output["save_solution"]
        if val is False:
            s.save_solution = None
        elif val is True:
            s.save_solution = "default"
        else:
            s.save_solution = Path(val)
    if "serve" in output:
        s.serve = output["serve"]

def _apply_cli(s: Settings, cli: dict) -> None:
    if cli.get("gtfs_folder") is not None:
        s.gtfs_folder = cli["gtfs_folder"]
    if cli.get("graph") is not None:
        s.graph = cli["graph"]
    if cli.get("matrix") is not None:
        s.matrix = cli["matrix"]
    if cli.get("solution") is not None:
        s.solution = cli["solution"]
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
    if cli.get("save_matrix") is not None:
        s.save_matrix = cli["save_matrix"]  # None, "default", or Path
    if cli.get("save_solution") is not None:
        s.save_solution = cli["save_solution"]
    if cli.get("serve"):
        s.serve = True


def _parse_start(value: list[str] | str | None) -> list[int] | str | None:
    if value is None:
        return None
    if value == ["all"] or value == "all":
        return "all"
    return [int(v) for v in value]


def resolve_save_path(setting: Path | str | None, default_dir: Path, filename: str) -> Path | None:
    if setting is None:
        return None
    if setting == "default":
        return default_dir / filename
    return setting
