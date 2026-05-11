### path_reconstructor.py
### Reconstructs the final result path based on the mode

import numpy as np
from hamilbus.datamodels import Line, BusNetworkGraph


class PathReconstructor:
    """Implement methods to go from raw solutions out of the solver,
    to lists of stops ids. Optionally reconstructs the real path.
    Main entry points : 
    - format_solution : from list of matrix indices to list of ids. Can reconstruct.
    - add_solution_to_graph : add solution to the graph as a line. Can format if needed."""
    def __init__(
        self,
        stops_index_to_id: dict[int, str],
        graph: BusNetworkGraph = None,
        path_matrix: np.ndarray = None,
    ):
        self.graph = graph
        self.stops_index_to_id = stops_index_to_id
        self.path_matrix = path_matrix
        if self.graph:
            self.ids_to_stops = {stop.id: stop for stop in self.graph.get_stops()}

    def convert_indices_to_ids(self, solution: list[int]) -> list[str]:
        """Convert the solution as a list of stops indices in the matrix (given by the solver),
        to a list of actual stop ids"""
        return [self.stops_index_to_id[stop_index] for stop_index in solution]

    def reconstruct_sparse_path(self, solution: list[int]) -> list[str]:
        """Reconstructs the real path from the path_matrix, only passing through existing edges.
        No need to go through convert_indices_to_ids as the path_matrix already contains stop indices."""
        real_solution_ids = []
        for u, v in zip(solution, solution[1:]):
            real_path = self.path_matrix[u, v]
            if len(real_solution_ids) > 1:
                # Keep the first node the first time, then cut it for the next paths to avoid [0, 1, 1, 2, 2...]
                real_path = real_path[1:]
            real_solution_ids += real_path
        return real_solution_ids

    def format_solution(self, solution: list[int], reconstruct: bool=False) -> list[str]:
        if reconstruct:
            return self.reconstruct_sparse_path(solution)
        else :
            return self.convert_indices_to_ids(solution)

    def convert_solution_ids_to_line(
        self,
        solution_ids: list[str],
        id: str = "solution",
        name: str = "Solution",
        color: str = "#FC1702",
    ) -> Line:
        """Create a Line object from the solution_ids"""
        solution_stops = [self.ids_to_stops[stop_id] for stop_id in solution_ids]
        line = Line(
            id=id,
            name=name,
            long_name=name,
            color=color,
            stops=solution_stops,
        )
        return line

    def add_solution_to_graph(
        self,
        solution: list[int],
        reconstruct: bool = False,
        format: bool = False,
        id: str = "solution",
        name: str = "Solution",
        color: str = "#FC1702",
    ):
        """Pipeline for the whole process : from raw solution out of the solver to new line in the graph."""
        if format:
            solution = self.format_solution(solution, reconstruct)
        solution_line = self.convert_solution_ids_to_line(solution, id, name, color)
        self.graph.add_line(solution_line)
