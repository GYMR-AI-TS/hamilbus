### base_solver.py
### Implements the BaseSolver ABC class

from abc import ABC, abstractmethod


class BaseSolver(ABC):
    @abstractmethod
    def solve(self):
        pass
