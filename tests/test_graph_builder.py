from hamilbus import graph_builder
from hamilbus.graph_builder import GraphBuilder
from hamilbus.datamodels import Stop, Line
from shapely.geometry import LineString
import pytest


def test_class_creation():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060),
        Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061),
    ]
    lines = [Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", stops=[stops[0], stops[1]])]
    graph_builder = GraphBuilder(stops, lines)
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
        Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060),
        Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061),
    ]
    lines = ["line1", "line2"]
    try:
        graph_builder = GraphBuilder(stops, lines)
        assert False, "Should have raised TypeError for wrong type of 'lines' parameter"
    except TypeError:
        pass  # Expected behavior


def test_build_lines():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006),
        Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-1.5007),
    ]
    shape = [(stops[0].lat, stops[0].lon), (stops[1].lat, stops[1].lon)]
    lines = [Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", shape=shape)]
    graph_builder = GraphBuilder(stops, lines)
    expected_points = [graph_builder.transformer.transform(lon, lat) for lat, lon in shape]
    expected_line = LineString(expected_points)
    assert graph_builder._line_shapes[0][0].equals_exact(expected_line, tolerance=1e-6)
    for got, expected in zip(graph_builder._line_shapes[0][1], expected_line.bounds):
        assert got == pytest.approx(expected, rel=1e-9, abs=1e-6)


def test_determine_belonging():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40, lon=-1),
        Stop(index=1, name="Stop 2", type="centroid", lat=39, lon=-2),
    ]
    shape = [(stops[0].lat, stops[0].lon), (stops[0].lat + 0.01, stops[0].lon + 0.01)]
    lines = [Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", shape=shape)]
    graph_builder = GraphBuilder(stops, lines)
    assert graph_builder.determine_belonging(stops[0], lines[0])
    assert stops[0].lines == lines
    assert not graph_builder.determine_belonging(stops[1], lines[0])
    assert stops[1].lines == []


def test_assign_stops_to_lines():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40, lon=-1),
        Stop(index=1, name="Stop 2", type="substation", lat=40.000100, lon=-1.000100),
        Stop(index=2, name="Stop 3", type="centroid", lat=39, lon=-2),
    ]
    shapes = [
        [(40, -1), (39, 0), (38, 1)],
        [(50, 5), (51, 6)],
    ]
    lines = [
        Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", shape=shapes[0]),
        Line(index=1, name="Line 2", long_name="Line 2 Long Name", color="blue", shape=shapes[1]),
    ]
    graph_builder = GraphBuilder(stops, lines)
    graph_builder.assign_stops_to_lines()
    assert stops[0].lines == lines[:1]
    assert stops[1].lines == lines[:1]
    assert stops[2].lines == []
    for stop in stops:
        assert lines[1] not in stop.lines
        # Empty lines attribute
        stop.lines = []
    # Retry but with a lower threshold
    graph_builder.assign_stops_to_lines(threshold=1)
    assert stops[0].lines == lines[:1]
    assert stops[1].lines == []


def test_merge_stops():
    lines = [
        Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red"),
        Line(index=1, name="Line 2", long_name="Line 2 Long Name", color="blue"),
    ]
    stops = [
        Stop(index=1_000_025, name="Stop 1", type="parent_station", lat=40, lon=-1, lines=[lines[0]]),
        Stop(index=2_000_032, name="Stop 1", type="substation", lat=41, lon=-2, lines=[lines[1]]),
    ]
    graph_builder = GraphBuilder(stops, lines)
    merged_stops = graph_builder.merge_stops()
    assert len(merged_stops) == 1
    assert merged_stops[0].index == 3_000_025
    assert merged_stops[0].name == "Stop 1"
    assert merged_stops[0].type == "centroid"
    assert merged_stops[0].lat == 40.5
    assert merged_stops[0].lon == -1.5
    assert merged_stops[0].lines == lines
    assert merged_stops[0].parent_station_idx is None


def test_order_stops():
    shape = [(40, 1), (40, 2), (40, 3)]
    lines = [
        Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", shape=shape),
        Line(index=1, name="Line 2", long_name="Line that touches no stop", color="blue"),
    ]
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40, lon=1, lines=[lines[0]]),
        Stop(index=1, name="Stop 2", type="substation", lat=40, lon=2, lines=[lines[0]]),
        Stop(index=2, name="Stop 3", type="centroid", lat=40, lon=1.5, lines=[lines[0]]),
        Stop(index=3, name="Stop 3.5", type="centroid", lat=40, lon=2),
    ]
    graph_builder = GraphBuilder(stops, lines)
    graph_builder.order_stops()
    assert lines[0].stops == [stops[0], stops[2], stops[1]]
    assert lines[1].stops == []


def test_build_graph():
    stops = [
        Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006),
        Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-1.5007),
        Stop(index=2, name="Stop 3", type="substation", lat=40.7130, lon=-1.5008),
        Stop(index=3, name="Stop 4", type="substation", lat=40.7131, lon=-1.5009),
    ]
    lines = [
        Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", stops=[stops[0], stops[1]]),
        Line(index=1, name="Line 2", long_name="Line 2 Long Name", color="blue", stops=[stops[0], stops[2]]),
        Line(index=2, name="Line 3", long_name="Line 3 Long Name", color="green", stops=[stops[2], stops[3]]),
        Line(index=3, name="Line 4", long_name="Line 4 Long Name", color="yellow", stops=[stops[1], stops[2], stops[3]]),
    ]
    graph_builder = GraphBuilder(stops, lines)
    graph = graph_builder.build_graph()
    assert len(graph.get_stops()) == 4
    assert len(graph.get_edges()) == 5
    assert graph.get_stops()[0].index == 0
    assert graph.get_stops()[1].index == 1
    assert graph.get_stops()[2].index == 2
    assert graph.get_stops()[3].index == 3
    assert graph.get_edges()[0][0].index == 0
    assert graph.get_edges()[0][1].index == 1
    assert graph.get_edges()[1][0].index == 0
    assert graph.get_edges()[1][1].index == 2
