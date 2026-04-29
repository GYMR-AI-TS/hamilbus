from hamilbus.graph_builder import GraphBuilder
from hamilbus.datamodels import Stop, Line


def test_class_creation():
    stops = [
        Stop(id="0", name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060),
        Stop(id="1", name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061),
    ]
    lines = [Line(id="0", name="Line 1", long_name="Line 1 Long Name", color="red", stops=[stops[0], stops[1]])]
    trips_by_lines, stops_by_trips = {}, {}
    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    assert graph_builder.stops == stops
    assert graph_builder.lines == lines


def test_class_creation_failure_1():
    try:
        _ = GraphBuilder()
        assert False, "Should have raised ValueError for missing 'stops' parameter"
    except TypeError:
        pass  # Expected behavior


def test_class_creation_failure_2():
    stops = [
        Stop(id="0", name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060),
        Stop(id="1", name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061),
    ]
    lines = ["line1", "line2"]
    try:
        _ = GraphBuilder(stops, lines)
        assert False, "Should have raised TypeError for wrong type of 'lines' parameter"
    except TypeError:
        pass  # Expected behavior


def test_merge_stops():
    stops = [
        Stop(id="1", name="Stop 1", type="parent_station", lat=40, lon=-1),
        Stop(id="2", name="Stop 2", type="substation", lat=41, lon=-2, parent_station_id="1"),
        Stop(id="3", name="Stop 3", type="substation", lat=42, lon=-3, parent_station_id="2"),
        Stop(id="4", name="Stop 1", type="substation", lat=43, lon=-4, parent_station_id="2"),
    ]
    lines, trips_by_lines, stops_by_trips = [], {}, {}
    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    graph_builder.merge_stops()
    merged_stops = graph_builder.merged_stops
    assert len(merged_stops) == 2
    assert merged_stops[0].id == "1"
    assert merged_stops[0].name == "Stop 1"
    assert merged_stops[0].type == "centroid"
    assert merged_stops[0].lat == 40.5
    assert merged_stops[0].lon == -1.5
    assert merged_stops[0].parent_station_id is None
    assert merged_stops[1].id == "3"
    assert merged_stops[1].name == "Stop 3"
    assert merged_stops[1].type == "centroid"
    assert merged_stops[1].lat == 42.5
    assert merged_stops[1].lon == -3.5
    assert merged_stops[1].parent_station_id is None


def test_build_graph():
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
    assert len(graph.get_stops()) == 4
    assert len(graph.get_edges()) == 4
    assert graph.get_stops()[0].id == "0"
    assert graph.get_stops()[1].id == "1"
    assert graph.get_stops()[2].id == "2"
    assert graph.get_stops()[3].id == "3"
    assert graph.get_edges()[0][0].id == "0"
    assert graph.get_edges()[0][1].id == "1"
    assert graph.get_edges()[1][0].id == "0"
    assert graph.get_edges()[1][1].id == "2"


def count_unique_values(d: dict):
    """Helper to count unique values of a dict with unhashable values like Stops"""
    unique = []
    for v in d.values():
        if v not in unique:
            unique.append(v)
    return len(unique)


def test_build_graph_after_merge_stops():
    stops = [
        Stop(id="0", name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006),
        Stop(id="1", name="Stop 2", type="substation", lat=40.7129, lon=-1.5007, parent_station_id="0"),
        Stop(id="2", name="Stop 3", type="parent_station", lat=40.7130, lon=-1.5008),
        Stop(id="3", name="Stop 4", type="substation", lat=40.7131, lon=-1.5009, parent_station_id="2"),
        Stop(id="4", name="Stop 3", type="parent_station", lat=40.7130, lon=-1.5008),
        Stop(id="5", name="Stop 4", type="substation", lat=40.7131, lon=-1.5009, parent_station_id="4"),
    ]
    lines = [
        Line(id="0", name="Line 1", long_name="Line 1 Long Name", color="red"),
        Line(id="1", name="Line 2", long_name="Line 2 Long Name", color="blue"),
        Line(id="2", name="Line 3", long_name="Line 3 Long Name", color="green"),
    ]
    trips_by_lines = {
        "0": ["trip0", "trip3"],
        "1": ["trip1"],
        "2": ["trip2"],
    }
    stops_by_trips = {
        "trip0": ["0", "2", "4"],  # 2 new edges
        "trip1": ["1", "3", "5"],  # Same as trip0, 0 new edges
        "trip2": ["1", "4"],  # 1 new edge
        "trip3": ["4", "3", "2", "1", "0"],  # 2 new self-edges
    }
    graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
    assert count_unique_values(graph_builder.stop_id_to_centroid) == 6
    graph_builder.merge_stops()
    assert count_unique_values(graph_builder.stop_id_to_centroid) == 3

    graph = graph_builder.build_graph()
    assert len(graph.get_stops()) == 3
    assert len(graph.get_edges()) == 5
    assert graph.get_stops()[0].id == "0"
    assert graph.get_stops()[1].id == "2"
    assert graph.get_stops()[2].id == "4"
    # Graph edges are returned ordered by nodes
    assert graph.get_edges()[0][0].id == "0"
    assert graph.get_edges()[0][1].id == "2"
    assert graph.get_edges()[1][0].id == "0"
    assert graph.get_edges()[1][1].id == "0"
    assert graph.get_edges()[2][0].id == "0"
    assert graph.get_edges()[2][1].id == "4"
    assert graph.get_edges()[3][0].id == "2"
    assert graph.get_edges()[3][1].id == "4"
    assert graph.get_edges()[4][0].id == "2"
    assert graph.get_edges()[4][1].id == "2"

    assert graph.get_stops()[0].lines == lines
    # Line 1 doesn't create new edges since it goes through the same stops as line 0,
    # but is still added to stop.lines for these stops
    assert graph.get_stops()[1].lines == lines[:2]
    assert graph.get_stops()[2].lines == lines
    # stops referenced in the graph's nodes and stops in the graph builder are the same objects :
    assert graph_builder.merged_stops[2].lines == lines

    assert graph_builder.lines[0].stops == graph_builder.merged_stops
    assert graph_builder.lines[1].stops == graph_builder.merged_stops
    assert graph_builder.lines[2].stops == graph_builder.merged_stops[:1] + graph_builder.merged_stops[2:]
