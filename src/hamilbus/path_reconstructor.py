### path_reconstructor.py
### Reconstructs the final result path based on the mode

import numpy as np
from hamilbus.datamodels import Line, BusNetworkGraph

class PathReconstructor:
    def __init__(self, graph: BusNetworkGraph, stops_index_to_id: dict[int, str], path_matrix: np.ndarray = None):
        self.graph = graph
        self.stops_index_to_id = stops_index_to_id
        self.path_matrix = path_matrix

    def convert_solution_to_line(self, solution: list[int]) -> Line:
        ids_to_stops = {stop.id: stop for stop in self.graph.get_stops()}
        solution_stops = []
        for stop_index in solution:
            stop_id = self.stops_index_to_id[stop_index]
            solution_stops.append(ids_to_stops[stop_id])
        line = Line(
            id="Solution",
            name="Solution",
            long_name="Solution",
            color="#8100FF",
            stops=solution_stops,
        )
        return line

    def add_solution_to_graph(self, solution: list[int]):
        solution_line = self.convert_solution_to_line(solution)
        self.graph.add_line(solution_line)

    def reconstruct_sparse_path(self, solution) -> list[Stop]:
        ids_to_stops = {stop.id: stop for stop in self.graph.get_stops()}
        real_solution_stops = []
        for u, v in zip(solution, solution[1:]):
            real_path = self.path_matrix[u, v]
            for stop_id in real_path:
                stop = ids_to_stops[stop_id]
                real_solution_stops.append(stop)
        return real_solution_stops
