### path_reconstructor.py
### Reconstructs the final result path based on the mode

import numpy as np
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


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

    def convert_solution_to_line(
        self,
        solution: list[int],
        id: str = "solution",
        name: str = "Solution",
        color: str = "#FC1702",
    ) -> Line:
        solution_stops = []
        for stop_index in solution:
            stop_id = self.stops_index_to_id[stop_index]
            solution_stops.append(self.ids_to_stops[stop_id])
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
        id: str = "solution",
        name: str = "Solution",
        color: str = "#FC1702",
    ):
        solution_line = self.convert_solution_to_line(solution, id, name, color)
        self.graph.add_line(solution_line)

    def reconstruct_sparse_path(self, solution) -> list[Stop]:
        real_solution_stops = []
        for u, v in zip(solution, solution[1:]):
            real_path = self.path_matrix[u, v]
            for stop_id in real_path:
                stop = self.ids_to_stops[stop_id]
                real_solution_stops.append(stop)
        return real_solution_stops
