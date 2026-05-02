import json
import numpy as np
from pathlib import Path


def save_array(arr: np.ndarray, name: str | Path) -> Path:
    """Save a NumPy array to disk. Extension is set automatically (.npy) if omitted"""
    path = Path.cwd() / name
    path = path.with_suffix(".npy")
    np.save(path, arr)
    return path.resolve()


def load_array(name: str | Path) -> np.ndarray:
    """Load a NumPy array from a .npz file in current working directory"""
    path = Path.cwd() / name
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix == ".npy":
        return np.load(path)
    else:
        raise ValueError(f"Unsupported extension: {path.suffix!r}. Use .npy or .npz")


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