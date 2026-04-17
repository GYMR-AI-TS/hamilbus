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
    