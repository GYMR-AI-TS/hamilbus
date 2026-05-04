### config.py
### 

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Settings:
    # --- defaults live here ---
    gtfs_folder: Path = Path("./data")
    complete_graph: bool = True
    distance_method: str = "euclidean"
    ignored_lines: list[str] = field(default_factory=list)
    save_solution: bool = True
    save_matrix: bool = True
    output_dir: Path = Path("./results")
    solver: str = "nearest_neighbor"
    solution: Path | None = None


def load_settings(config_path: Path | None, cli_overrides: dict) -> Settings:
    s = Settings()  # 1. start from defaults

    if config_path and config_path.exists():
        with open(config_path, "rb") as f:
            toml_data = tomllib.load(f)  # 2. override with config file
        _apply_toml(s, toml_data)

    _apply_cli(s, cli_overrides)  # 3. override with CLI

    return s


def _apply_toml(s: Settings, data: dict) -> None:
    # TOML is nested, so we flatten it
    graph = data.get("graph", {})
    if "complete" in graph:
        s.complete_graph = graph["complete"]
    if "distance_method" in graph:
        s.distance_method = graph["distance_method"]
    # ... etc


def _apply_cli(s: Settings, cli: dict) -> None:
    # argparse sets missing flags to None, so we only apply what was explicitly passed
    if cli.get("gtfs_folder") is not None:
        s.gtfs_folder = cli["gtfs_folder"]
    if cli.get("solver") is not None:
        s.solver = cli["solver"]
    # ... etc