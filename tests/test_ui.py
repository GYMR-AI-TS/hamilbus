import json
from hamilbus.datamodels import Stop, Line
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web.app import api_stops, api_lines, set_network, set_graph_network


def test_serializers():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006),
        Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-1.5007),
        Stop(index=2, name="Stop 3", type="substation", lat=40.7130, lon=-1.5008),
        Stop(index=3, name="Stop 4", type="substation", lat=40.7131, lon=-1.5009),
        Stop(index=4, name="Stop 5", type="substation", lat=52, lon=-12),
    ]
    lines = [
        Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", stops=[stops[0], stops[1]]),
        Line(index=1, name="Line 2", long_name="Line 2 Long Name", color="blue", stops=[stops[0], stops[2]]),
        Line(index=2, name="Line 3", long_name="Line 3 Long Name", color="green", stops=[stops[2], stops[3]]),
        Line(index=3, name="Line 4", long_name="Line 4 Long Name", color="yellow", stops=[stops[1], stops[2], stops[3]]),
    ]

    set_network(stops, lines)
    stops_json_response_network = api_stops()
    lines_json_response_network = api_lines()

    graph_builder = GraphBuilder(stops, lines)
    graph = graph_builder.build_graph()

    set_graph_network(graph)
    stops_json_response_graph = api_stops()
    lines_json_response_graph = api_lines()

    assert stops_json_response_network.status_code == stops_json_response_graph.status_code
    # assert json.loads(stops_json_response_network.body) == json.loads(stops_json_response_graph.body)

    assert lines_json_response_network.status_code == lines_json_response_graph.status_code
    # assert json.loads(lines_json_response_network.body) == json.loads(lines_json_response_graph.body)