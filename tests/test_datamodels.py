from math import sqrt
from pathlib import Path
import hamilbus as hbus
import networkx as nx

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "hamilbus" / "data"
STOPS_PATH = DATA_DIR / "stops.txt"
ROUTES_PATH = DATA_DIR / "routes.txt"
SHAPES_PATH = DATA_DIR / "shapes.txt"

stops = hbus.reader.load_stops(STOPS_PATH)
lines = hbus.reader.load_lines(ROUTES_PATH, SHAPES_PATH)

print("Number of stops : ", len(stops))
print("Number of lines : ", len(lines))
print(list(stops.values())[0])
print(list(stops.values())[2000])
print(list(lines.values())[5])


def test_parsers():
    id = hbus.reader.parse_stop_id("FR_NAOLIB:StopPlace:194")
    assert id == 1000194


def test_stops_number():
    stops = hbus.reader.load_stops(STOPS_PATH)
    assert len(stops) == 3741


def test_lines_number():
    lines = hbus.reader.load_lines(ROUTES_PATH, SHAPES_PATH)
    assert len(lines) == 109


def test_stop_creation_success():
    stop = hbus.Stop(
        index=0,
        name="Stop 1",
        type="parent_station",
        lat=40.7128,
        lon=-74.0060,
    )
    assert stop.index == 0
    assert stop.name == "Stop 1"
    assert stop.type == "parent_station"
    assert stop.lat == 40.7128
    assert stop.lon == -74.0060
    assert stop.lines == []
    assert stop.parent_station_idx is None


def test_stop_creation_failure():
    try:
        hbus.Stop(
            index=0,
            name="Stop 1",
            lat=40.7128,
            lon=-74.0060,
        )
        assert False, "Should have raised TypeError for missing 'type' parameter"
    except TypeError:
        pass  # Expected behavior


def test_line_creation():
    line = hbus.Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red")
    assert line.index == 0
    assert line.name == "Line 1"
    assert line.long_name == "Line 1 Long Name"
    assert line.color == "red"
    assert line.shape == []
    assert line.stops == []


def test_line_creation_failure():
    try:
        hbus.Line(index=0, long_name="Line 1 Long Name", color="red")
        assert False, "Should have raised TypeError for missing 'name' parameter"
    except TypeError:
        pass  # Expected


def test_bus_network_graph_creation():
    graph = hbus.BusNetworkGraph()
    assert isinstance(graph.graph, nx.MultiGraph)


def test_add_stop_to_graph():
    graph = hbus.BusNetworkGraph()
    stop = hbus.Stop(
        index=0,
        name="Stop 1",
        type="parent_station",
        lat=40.7128,
        lon=-74.0060,
    )
    graph.add_stop(stop)
    assert graph.graph.has_node(stop.index)
    assert graph.graph.nodes[stop.index]["stop"] == stop


def test_add_edge_to_graph():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        index=0,
        name="Stop 1",
        type="parent_station",
        lat=40.7128,
        lon=-74.0060,
    )
    stop2 = hbus.Stop(
        index=1,
        name="Stop 2",
        type="parent_station",
        lat=40.7129,
        lon=-74.0061,
    )
    graph.add_stop(stop1)
    graph.add_stop(stop2)
    graph.add_edge(
        stop1,
        stop2,
        line=hbus.Line(
            index=0, name="Line 1", long_name="Line 1 Long Name", color="red"
        ),
    )
    assert graph.graph.has_edge(stop1.index, stop2.index)
    assert graph.graph[stop1.index][stop2.index][0]["line"].index == 0
    expected_distance = sqrt(
        (stop1.lat - stop2.lat) ** 2 + (stop1.lon - stop2.lon) ** 2
    )
    assert graph.graph[stop1.index][stop2.index][0]["distance"] == expected_distance


def test_get_stops_returns_all_stops():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060
    )
    stop2 = hbus.Stop(
        index=1, name="Stop 2", type="substation", lat=40.7129, lon=-74.0061
    )
    graph.add_stop(stop1)
    graph.add_stop(stop2)

    stops = graph.get_stops()
    assert stop1 in stops
    assert stop2 in stops
    assert len(stops) == 2


def test_get_edges_returns_edge_attributes():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060
    )
    stop2 = hbus.Stop(
        index=1, name="Stop 2", type="substation", lat=40.7129, lon=-74.0061
    )
    line = hbus.Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red")

    graph.add_stop(stop1)
    graph.add_stop(stop2)
    graph.add_edge(stop1, stop2, line=line)

    edges = graph.get_edges()
    assert len(edges) == 1
    source, target, data = edges[0]
    assert source == stop1
    assert target == stop2
    assert data["line"] == line
    expected_distance = sqrt(
        (stop1.lat - stop2.lat) ** 2 + (stop1.lon - stop2.lon) ** 2
    )
    assert data["distance"] == expected_distance


def test_add_line_connects_stops_and_adds_nodes():
    graph = hbus.BusNetworkGraph()
    stops = [
        hbus.Stop(
            index=i,
            name=f"Stop {i}",
            type="parent_station",
            lat=40.7128 + i * 0.0001,
            lon=-74.0060 - i * 0.0001,
        )
        for i in range(3)
    ]
    line = hbus.Line(
        index=0, name="Line 1", long_name="Line 1 Long Name", color="red", stops=stops
    )

    graph.add_line(line)

    assert graph.graph.has_node(0)
    assert graph.graph.has_node(1)
    assert graph.graph.has_node(2)
    assert graph.graph.number_of_edges() == 2
    assert graph.graph[0][1][0]["line"] == line
    assert graph.graph[1][2][0]["line"] == line


def test_fully_connected_graph_preserves_edge_data():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060
    )
    stop2 = hbus.Stop(
        index=1, name="Stop 2", type="substation", lat=40.7129, lon=-74.0061
    )

    graph.add_stop(stop1)
    graph.add_stop(stop2)

    fully_connected = graph.fully_connected_graph()
    assert isinstance(fully_connected, nx.Graph)
    assert fully_connected.has_edge(stop1.index, stop2.index)
    assert fully_connected[stop1.index][stop2.index]["line"].name == "Direct Connection"
