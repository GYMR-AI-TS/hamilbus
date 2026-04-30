from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""

    DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
    STOPS_PATH = DATA_DIR / "stops.txt"
    ROUTES_PATH = DATA_DIR / "routes.txt"
    TRIPS_PATH = DATA_DIR / "trips.txt"
    STOP_TIMES_PATH = DATA_DIR / "stop_times.txt"
    stops = reader.load_stops(STOPS_PATH)
    lines = reader.load_lines(ROUTES_PATH)
    trips_by_lines = reader.load_trips_per_line(TRIPS_PATH)
    stops_by_trips = reader.load_stops_per_trip(STOP_TIMES_PATH)

    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    graph_builder.merge_stops()
    graph = graph_builder.build_graph()

    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
