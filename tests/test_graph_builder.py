from hamilbus.graph_builder import GraphBuilder
from hamilbus.datamodels import Stop, Line
from shapely.geometry import LineString
import pytest


def test_class_creation():
    stops = [Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060), Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061)]
    lines = [Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", stops=[stops[0], stops[1]])]
    graph_builder = GraphBuilder(stops, lines)
    assert graph_builder.stops == stops
    assert graph_builder.lines == lines

def test_class_creation_failure_1():
    try:
        graph_builder = GraphBuilder()
        assert False, "Should have raised ValueError for missing 'stops' parameter"
    except TypeError:
        pass  # Expected behavior

def test_class_creation_failure_2():
    stops = [Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-74.0060), Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-74.0061)]
    lines = ["line1", "line2"]
    try:
        graph_builder = GraphBuilder(stops, lines)
        assert False, "Should have raised TypeError for wrong type of 'lines' parameter"
    except TypeError:
        pass  # Expected behavior

def test_build_lines():
    stops = [Stop(index=0, name="Stop 1", type="parent_station", lat=40.7128, lon=-1.5006), Stop(index=1, name="Stop 2", type="parent_station", lat=40.7129, lon=-1.5007)]
    shape = [(stops[0].lat, stops[0].lon), (stops[1].lat, stops[1].lon)]
    lines = [Line(index=0, name="Line 1", long_name="Line 1 Long Name", color="red", shape=shape)]
    graph_builder = GraphBuilder(stops, lines)
    expected_points = [graph_builder.project_lonlat_to_meters(lon, lat) for lat, lon in shape]
    expected_line = LineString(expected_points)
    assert graph_builder._line_shapes[0].equals_exact(expected_line, tolerance=1e-6)
    for got, expected in zip(graph_builder._line_bounds[0], expected_line.bounds):
        assert got == pytest.approx(expected, rel=1e-9, abs=1e-6)