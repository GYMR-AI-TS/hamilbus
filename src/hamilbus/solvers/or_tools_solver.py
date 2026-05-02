### or_tools_solver.py
### Implement a simple TSP solver using Google's OR-Tools

import time
import numpy as np
from hamilbus.solvers.base_solver import BaseSolver
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class ORToolsSolver(BaseSolver):
    def __init__(self, distance_matrix: list[list[float]], time_limit_seconds: int = 30):
        self.distance_matrix = self._transform_distance_matrix(distance_matrix)

        self.time_limit_seconds = time_limit_seconds

        self.index_manager = pywrapcp.RoutingIndexManager(len(self.distance_matrix), 1, 0)
        self.routing_model = pywrapcp.RoutingModel(self.index_manager)

        def distance_callback(from_index, to_index):
            from_node = self.index_manager.IndexToNode(from_index)
            to_node = self.index_manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]

        transit_callback_index = self.routing_model.RegisterTransitCallback(distance_callback)
        self.routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        # GLS requires a local search metaheuristic
        self.search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        self.search_parameters.time_limit.seconds = time_limit_seconds


    def _transform_distance_matrix(self, distance_matrix):
        # Count reachable nodes for each node (non-inf values)
        reachable_counts = np.sum(~np.isinf(distance_matrix), axis=1)
        # Find the most common count
        main_size = np.max(reachable_counts)
        # Identify nodes that can't reach most of the graph
        indices = np.where(reachable_counts < main_size)[0]
        # Remove the corresponding rows and columns
        clean_matrix = np.delete(distance_matrix, indices, axis=0)
        clean_matrix = np.delete(clean_matrix, indices, axis=1)
        # Round and cast as int
        return clean_matrix.round().astype(int)

    def solve(self):
        n_improvements = 0
        best_cost = [float("inf")]  # list so the closure can mutate it
        start_time = time.time()

        def on_solution():
            nonlocal n_improvements
            current = self.routing_model.CostVar().Value()
            if current < best_cost[0]:
                best_cost[0] = current
                n_improvements += 1
                elapsed = time.time() - start_time
                print(
                    f"\r[{elapsed:5.1f}s] #{n_improvements:3d} — best: {best_cost[0]:,}",
                    end="",
                    flush=True,
                )

        self.routing_model.AddAtSolutionCallback(on_solution)

        solution = self.routing_model.SolveWithParameters(self.search_parameters)
        elapsed = time.time() - start_time
        print(f"\nSolved in {elapsed:.1f}s — final cost: {best_cost[0]:,}")

        if solution:
            return self.unpack_solution(solution)

    def unpack_solution(self, solution):
        """Unpacks the solution into a list of nodes and a distance"""
        path = []
        index = self.routing_model.Start(0)
        route_distance = 0
        while not self.routing_model.IsEnd(index):
            path.append(self.index_manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(self.routing_model.NextVar(index))
            route_distance += self.routing_model.GetArcCostForVehicle(
                previous_index, index, 0
            )
        path.append(self.index_manager.IndexToNode(index))
        return path, route_distance

    def print_solution(self, solution):
        """Prints solution on console."""
        print(f"Objective: {solution.ObjectiveValue()} meters")
        index = self.routing_model.Start(0)
        plan_output = "Route :\n"
        route_distance = 0
        while not self.routing_model.IsEnd(index):
            plan_output += f" {self.index_manager.IndexToNode(index)} ->"
            previous_index = index
            index = solution.Value(self.routing_model.NextVar(index))
            route_distance += self.routing_model.GetArcCostForVehicle(
                previous_index, index, 0
            )
        plan_output += f" {self.index_manager.IndexToNode(index)}\n"
        plan_output += f"Route distance: {route_distance} meters\n"
        print(plan_output)
