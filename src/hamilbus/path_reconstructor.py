### path_reconstructor.py
### Reconstructs the final result path based on the mode

import numpy as np
from hamilbus.datamodels import Line, BusNetworkGraph


class PathReconstructor:
    def __init__(
        self,
        graph: BusNetworkGraph,
        stops_index_to_id: dict[int, str],
        path_matrix: np.ndarray = None,
    ):
        self.graph = graph
        self.stops_index_to_id = stops_index_to_id
        self.path_matrix = path_matrix
        self.ids_to_stops = {stop.id: stop for stop in self.graph.get_stops()}

    def convert_indices_to_ids(self, solution: list[int]) -> list[str]:
        """Convert the solution as a list of stops indices in the matrix (given by the solver),
        to a list of actual stop ids"""
        return [self.stops_index_to_id[stop_index] for stop_index in solution]

    def reconstruct_sparse_path(self, solution) -> list[str]:
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
        id: str = "solution",
        name: str = "Solution",
        color: str = "#FC1702",
    ):
        """Pipeline for the whole process : from raw solution out of the solver to new line in the graph."""
        if reconstruct:
            solution_ids = self.reconstruct_sparse_path(solution)
        else:
            solution_ids = self.convert_indices_to_ids(solution)
        solution_line = self.convert_solution_ids_to_line(solution_ids, id, name, color)
        self.graph.add_line(solution_line)
