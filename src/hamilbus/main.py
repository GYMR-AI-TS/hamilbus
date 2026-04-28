from pathlib import Path
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""

    DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
    STOPS_PATH = DATA_DIR / "stops.txt"
    ROUTES_PATH = DATA_DIR / "routes.txt"
    SHAPES_PATH = DATA_DIR / "shapes.txt"
    stops = reader.load_stops(STOPS_PATH)
    lines = reader.load_lines(ROUTES_PATH, SHAPES_PATH)

    graph_builder = GraphBuilder(stops, lines)
    graph_builder.assign_stops_to_lines()
    graph_builder.merge_stops()
    graph_builder.order_stops()
    graph = graph_builder.build_graph()

    set_graph(graph)
    run_server(host="127.0.0.1", port=3000)


if __name__ == "__main__":
    main()
