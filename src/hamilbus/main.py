from .web import run_server, set_network
from .fake_network import _create_fake_network


def main() -> None:
    """Start the Hamilbus local web viewer on port 3000."""

    # network = NetworkBuilder.build("path/to/data/base.txt")
    stops, lines = (
        _create_fake_network()
    )  # Replace with real network | stops, lines = NetworkBuilder.stops_and_lines()
    set_network(stops, lines)

    run_server(host="127.0.0.1", port=3000)
from hamilbus.graph_builder import GraphBuilder
import hamilbus.reader as reader
from pathlib import Path


def main():
    DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
    STOPS_PATH = DATA_DIR / "stops.txt"
    ROUTES_PATH = DATA_DIR / "routes.txt"
    SHAPES_PATH = DATA_DIR / "shapes.txt"
    stops = reader.load_stops(STOPS_PATH)
    lines = reader.load_lines(ROUTES_PATH, SHAPES_PATH)

    builder = GraphBuilder(stops, lines)
    builder.assign_stops_to_lines()
    builder.stops = builder.merge_stops_by_name()
    builder.order_stops()
    graph = builder.build_graph()
    print(graph)


if __name__ == "__main__":
    main()
