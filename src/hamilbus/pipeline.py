### pipeline.py
### Orchestrates operations

from pathlib import Path
from hamilbus.config import Settings
import hamilbus.reader as reader
from hamilbus.graph_builder import GraphBuilder
from hamilbus.web import run_server, set_graph_network

def serve(settings: Settings):
        """Start the Hamilbus local web viewer on port 3000."""
        if settings.graph:
            # Load an already saved graph
            # load_graph(path)
            pass
        else :
            # Create the graph from the GTFS files
            DATA_DIR = Path(__file__).resolve().parents[1] / "hamilbus" / "data"
            # or settings.gtfs_folder
            stops, lines, trips_by_lines, stops_by_trips = reader.load_gtfs(DATA_DIR)
            graph_builder = GraphBuilder(stops, lines, trips_by_lines, stops_by_trips)
            graph_builder.merge_stops()
            graph = graph_builder.build_graph()
        
        if settings.solution:
            # Load an already saved solution and add it to the graph
            pass

        # Run the server
        set_graph_network(graph)
        run_server(host="127.0.0.1", port=3000)

def run_solver(settings: Settings):
    pass

def run_pipeline(settings: Settings):
    pass