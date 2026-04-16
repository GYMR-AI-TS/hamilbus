from hamilbus import reader

stops = reader.load_stops(r"src\hamilbus\data\stops.txt")
lines = reader.load_lines(r"src\hamilbus\data\routes.txt", r"src\hamilbus\data\shapes.txt")

print("Number of stops : ", len(stops))
print("Number of lines : ", len(lines))
print(list(stops.values())[0])
print(list(stops.values())[2000])
print(list(lines.values())[5])