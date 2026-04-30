from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""

    DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
    stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(DATA_DIR)

    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    graph_builder.merge_stops()
    graph = graph_builder.build_graph()

    set_graph_network(graph)
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
