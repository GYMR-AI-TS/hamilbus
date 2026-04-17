from pathlib import Path
from hamilbus import reader

DATA_DIR = Path(__file__).resolve().parents[1] / "src" / "hamilbus" / "data"
STOPS_PATH = DATA_DIR / "stops.txt"
ROUTES_PATH = DATA_DIR / "routes.txt"
SHAPES_PATH = DATA_DIR / "shapes.txt"

stops = reader.load_stops(STOPS_PATH)
lines = reader.load_lines(ROUTES_PATH, SHAPES_PATH)

print("Number of stops : ", len(stops))
print("Number of lines : ", len(lines))
print(list(stops.values())[0])
print(list(stops.values())[2000])
print(list(lines.values())[5])

def test_parsers():
   id = reader.parse_stop_id("FR_NAOLIB:StopPlace:194")
   assert id == 1000194

def test_stops_number():
   stops = reader.load_stops(STOPS_PATH)
   assert len(stops) == 3741

def test_lines_number():
   lines = reader.load_lines(ROUTES_PATH, SHAPES_PATH)
   assert len(lines) == 109