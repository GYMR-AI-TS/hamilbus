from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.helpers import save_array, load_array, save_dict, load_dict, save_list
from hamilbus.web import run_server, set_graph_network
from hamilbus.solvers.or_tools_solver import ORToolsSolver
from hamilbus.distance_matrix import compute_distance_matrix

def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""
    # Check if there's already a distance_matrix saved
    path = Path.cwd() / "distance_matrix.npy"
    if path.exists():
        distance_matrix = load_array("distance_matrix.npy")
    else :
        # Load the raw data
        DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
        stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(DATA_DIR)
        # Build the graph
        graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
        graph_builder.merge_stops()
        graph = graph_builder.build_graph()
        # Compute the distance matrix
        distance_matrix, path_matrix, stop_index_to_id = compute_distance_matrix(graph)
        save_array(path_matrix, "path_matrix")
        save_array(distance_matrix, "distance_matrix")
        save_dict(stop_index_to_id, "stop_index_to_id")
    
    solver = ORToolsSolver(distance_matrix, time_limit_seconds=30)
    solution = solver.solve()
    save_list(solution, "solution")

    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)

if __name__ == "__main__":
    main()
