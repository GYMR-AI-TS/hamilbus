import json
import numpy as np
from pathlib import Path


def save_array(arr: np.ndarray, path: str | Path) -> Path:
    """Save a NumPy array to disk. Extension is set automatically (.npy) if omitted"""
    path = Path(path).with_suffix(".npy")
    if not path.is_absolute():
        path = Path.cwd() / path
    np.save(path, arr)
    return path.resolve()


def load_array(path: str | Path) -> np.ndarray:
    """Load a NumPy array from a .npy file. Defaults to current working directory if no absolute path is given"""
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix == ".npy":
        return np.load(path)
    else:
        raise ValueError(f"Unsupported extension: {path.suffix!r}. Use .npy.")


def save_dict(d: dict[float, str], path: str | Path) -> Path:
    """Saves a dict as a json file in the current working dir"""
    path = Path.cwd() / Path(path).with_suffix(".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in d.items()}, f, indent=2)
    return path.resolve()


def load_dict(path: str | Path) -> dict[float, str]:
    """Loads a dict from a json file in the current working dir"""
    path = Path(path).with_suffix(".json")
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, encoding="utf-8") as f:
        return {float(k): v for k, v in json.load(f).items()}


def save_list(lst: list, path: str | Path) -> Path:
    path = Path.cwd() / Path(path).with_suffix(".json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(lst, f, indent=2)
    return path.resolve()


def load_list(path: str | Path) -> list:
    path = Path(path).with_suffix(".json")
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
