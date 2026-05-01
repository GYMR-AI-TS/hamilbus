import json
from hamilbus.datamodels import Stop, Line
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web.app import api_stops, api_lines, set_network, set_graph_network


def test_serializers():
    stops = [
        Stop(id="0", name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006),
        Stop(id="1", name="Stop 2", type="parent_station", lat=40.7129, lon=-1.5007),
        Stop(id="2", name="Stop 3", type="substation", lat=40.7130, lon=-1.5008),
        Stop(id="3", name="Stop 4", type="substation", lat=40.7131, lon=-1.5009),
    ]
    lines = [
        Line(id="0", name="Line 1", long_name="Line 1 Long Name", color="red"),
        Line(id="1", name="Line 2", long_name="Line 2 Long Name", color="blue"),
        Line(id="2", name="Line 3", long_name="Line 3 Long Name", color="green"),
        Line(id="3", name="Line 4", long_name="Line 4 Long Name", color="yellow"),
    ]
    trips_by_lines = {
        "0": ["trip0"],
        "1": ["trip1"],
        "2": ["trip2"],
        "3": ["trip3"],
    }
    stops_by_trips = {
        "trip0": ["0", "1"],
        "trip1": ["0", "2"],
        "trip2": ["2", "3"],
        "trip3": ["1", "2", "3"],
    }

    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    graph = graph_builder.build_graph()

    # Network mode
    set_network(stops, lines)
    stops_json_response_network = api_stops()
    lines_json_response_network = api_lines()

    # Graph mode
    set_graph_network(graph)
    stops_json_response_graph = api_stops()
    lines_json_response_graph = api_lines()

    assert (
        stops_json_response_network.status_code == stops_json_response_graph.status_code
    )
    assert json.loads(stops_json_response_network.body) == json.loads(
        stops_json_response_graph.body
    )

    assert (
        lines_json_response_network.status_code == lines_json_response_graph.status_code
    )
    assert len(json.loads(lines_json_response_network.body)) == len(
        json.loads(lines_json_response_graph.body)
    )
