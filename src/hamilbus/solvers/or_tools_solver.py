### or_tools_solver.py
### Implement a simple TSP solver using Google's OR-Tools

from hamilbus.solvers.base_solver import BaseSolver
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


class ORToolsSolver(BaseSolver):
    def __init__(self, distance_matrix: list[list[float]]):
        # Create the routing index manager.
        # args : num_nodes, num_vehicles, depot (start and end)
        self.index_manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
        # Create Routing Model.
        self.routing_model = pywrapcp.RoutingModel(self.index_manager)

        def distance_callback(from_index, to_index):
            """Returns the distance between the two nodes."""
            # Convert from routing variable Index to distance matrix NodeIndex.
            from_node = self.index_manager.IndexToNode(from_index)
            to_node = self.index_manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = self.routing_model.RegisterTransitCallback(
            distance_callback
        )
        # Define cost of each arc. Here : simply the distance
        self.routing_model.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Setting first solution heuristic.
        self.search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        self.search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )

    def solve(self):
        # Solve the problem.
        solution = self.routing_model.SolveWithParameters(self.search_parameters)
        # Print solution on console.
        if solution:
            self.print_solution(solution)
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
