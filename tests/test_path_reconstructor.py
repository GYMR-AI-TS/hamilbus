import numpy as np
from hamilbus.path_reconstructor import PathReconstructor
from hamilbus.datamodels import Stop, Line, BusNetworkGraph


def test_convert_indices_to_ids():
    graph = BusNetworkGraph()
    stops_index_to_id = {1: "Stop1", 2: "Stop2", 3: "Stop3", 4: "Stop4"}
    reconstructor = PathReconstructor(graph, stops_index_to_id)
    indices = list(stops_index_to_id.keys())
    ids = list(stops_index_to_id.values())
    assert reconstructor.convert_indices_to_ids(indices) == ids


def test_reconstruct_sparse_path():
    stops = [
        Stop(id="Stop1", name="1", type="parent_station", lat=0, lon=0),
        Stop(id="Stop2", name="2", type="parent_station", lat=1, lon=1),
        Stop(id="Stop3", name="3", type="substation", lat=2, lon=2),
        Stop(id="Stop4", name="4", type="substation", lat=3, lon=3),
    ]
    graph = BusNetworkGraph()
    for stop in stops:
        graph.add_stop(stop)
    stops_index_to_id = {0: "Stop1", 1: "Stop2", 2: "Stop3", 3: "Stop4"}
    path_matrix = np.empty((4, 4), dtype=object)
    path_data = [
        [[0], ["Stop1", "Stop2"], ["Stop1", "Stop2", "Stop3"], ["Stop1", "Stop2", "Stop3", "Stop4"]],
        [["Stop2", "Stop1"], [1], ["Stop2", "Stop3"], ["Stop2", "Stop3", "Stop4"]],
        [["Stop3", "Stop2", "Stop1"], ["Stop3", "Stop2"], [2], ["Stop3", "Stop4"]],
        [["Stop4", "Stop3", "Stop2", "Stop1"], ["Stop4", "Stop3", "Stop2"], ["Stop4", "Stop3"], [3]],
    ]
    for i in range(4):
        for j in range(4):
            path_matrix[i, j] = path_data[i][j]
    reconstructor = PathReconstructor(graph, stops_index_to_id, path_matrix)

    solution = [0, 1, 3]  # Real path : 0, 1, 2, 3
    assert reconstructor.reconstruct_sparse_path(solution) == ["Stop1", "Stop2", "Stop3", "Stop4"]


def test_convert_solution_to_line():
    stops = [
        Stop(id="Stop1", name="1", type="parent_station", lat=0, lon=0),
        Stop(id="Stop2", name="2", type="parent_station", lat=0, lon=0),
        Stop(id="Stop3", name="3", type="substation", lat=0, lon=0),
        Stop(id="Stop4", name="4", type="substation", lat=0, lon=0),
    ]
    graph = BusNetworkGraph()
    for stop in stops:
        graph.add_stop(stop)
    stops_index_to_id = {1: "Stop1", 2: "Stop2", 3: "Stop3", 4: "Stop4"}
    reconstructor = PathReconstructor(graph, stops_index_to_id)

    solution = [3, 1, 2, 4]
    solution_ids = reconstructor.convert_indices_to_ids(solution)
    line = Line(
        id="solution", name="Solution", long_name="Solution", color="#FC1702", stops=[stops[2], stops[0], stops[1], stops[3]]
    )
    assert reconstructor.convert_solution_ids_to_line(solution_ids) == line


def test_add_solution_to_graph_complete():
    stops = [
        Stop(id="Stop1", name="1", type="parent_station", lat=0, lon=0),
        Stop(id="Stop2", name="2", type="parent_station", lat=0, lon=0),
        Stop(id="Stop3", name="3", type="substation", lat=0, lon=0),
        Stop(id="Stop4", name="4", type="substation", lat=0, lon=0),
    ]
    graph = BusNetworkGraph()
    for stop in stops:
        graph.add_stop(stop)
    stops_index_to_id = {1: "Stop1", 2: "Stop2", 3: "Stop3", 4: "Stop4"}
    reconstructor = PathReconstructor(graph, stops_index_to_id)

    solution = [3, 1, 2, 4]
    reconstructor.add_solution_to_graph(solution)
    assert graph.has_edge(stops[2].id, stops[0].id)
    assert graph.has_edge(stops[0].id, stops[1].id)
    assert graph.has_edge(stops[1].id, stops[3].id)


def test_add_solution_to_graph_sparse():
    stops = [
        Stop(id="Stop1", name="1", type="parent_station", lat=0, lon=0),
        Stop(id="Stop2", name="2", type="parent_station", lat=0, lon=0),
        Stop(id="Stop3", name="3", type="substation", lat=0, lon=0),
        Stop(id="Stop4", name="4", type="substation", lat=0, lon=0),
    ]
    graph = BusNetworkGraph()
    for stop in stops:
        graph.add_stop(stop)
    stops_index_to_id = {1: "Stop1", 2: "Stop2", 3: "Stop3", 4: "Stop4"}
    path_matrix = np.empty((4, 4), dtype=object)
    path_data = [
        [[0], ["Stop1", "Stop2"], ["Stop1", "Stop2", "Stop3"], ["Stop1", "Stop2", "Stop3", "Stop4"]],
        [["Stop2", "Stop1"], [1], ["Stop2", "Stop3"], ["Stop2", "Stop3", "Stop4"]],
        [["Stop3", "Stop2", "Stop1"], ["Stop3", "Stop2"], [2], ["Stop3", "Stop4"]],
        [["Stop4", "Stop3", "Stop2", "Stop1"], ["Stop4", "Stop3", "Stop2"], ["Stop4", "Stop3"], [3]],
    ]
    for i in range(4):
        for j in range(4):
            path_matrix[i, j] = path_data[i][j]
    reconstructor = PathReconstructor(graph, stops_index_to_id, path_matrix)

    solution = [2, 0, 3]  # Real path 2, 1, 0, 1, 2, 3
    reconstructor.add_solution_to_graph(solution, reconstruct=True)

    assert graph.has_edge(stops[0].id, stops[1].id)
    assert graph.has_edge(stops[1].id, stops[2].id)
    assert graph.has_edge(stops[2].id, stops[3].id)
    assert not graph.has_edge(stops[2].id, stops[0].id)
    assert not graph.has_edge(stops[0].id, stops[3].id)
