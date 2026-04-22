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


if __name__ == "__main__":
    main()
