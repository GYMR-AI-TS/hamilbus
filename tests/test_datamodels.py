from hamilbus import reader

stops = reader.load_stops(r"src\hamilbus\data\stops.txt")
lines = reader.load_lines(r"src\hamilbus\data\routes.txt", r"src\hamilbus\data\shapes.txt")

print("Number of stops : ", len(stops))
print("Number of lines : ", len(lines))
print(list(stops.values())[0])
print(list(stops.values())[2000])
print(list(lines.values())[5])

def test_parsers():
   id = reader.parse_stop_id("FR_NAOLIB:StopPlace:194")
   assert id == 1000194

def test_stops_number():
   stops = reader.load_stops(r"src\hamilbus\data\stops.txt")
   assert len(stops) == 3741

def test_lines_number():
   lines = reader.load_lines(r"src\hamilbus\data\routes.txt", r"src\hamilbus\data\shapes.txt")
   assert len(lines) == 109