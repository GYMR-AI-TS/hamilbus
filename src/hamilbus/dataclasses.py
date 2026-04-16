### dataclasses.py
### Defines the dataclasses for storing stops and lines info

from typing import Optional
from dataclasses import dataclass, field

@dataclass
class Stop:
    index: int
    name: str
    lon: float
    lat: float
    lines: list[int] = field(default_factory=list) 
    parent_station: Optional[int] = None

@dataclass
class Line:
    index: int
    name: str
    long_name: str
    color: str
    shape: list[tuple[float, float]] = field(default_factory=list)