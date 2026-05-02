import hamilbus as hbus


def generate_test_graph():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        id="0",
        name="Stop 1",
        type="parent_station",
        lat=0,
        lon=0,
    )
    stop2 = hbus.Stop(
        id="1",
        name="Stop 2",
        type="parent_station",
        lat=0,
        lon=1,
    )
    stop3 = hbus.Stop(
        id="2",
        name="Stop 3",
        type="parent_station",
        lat=1,
        lon=0,
    )
    line = hbus.Line(
        id="0",
        name="Line 1",
        long_name="Line 1",
        color="#93A14E",
        stops=[stop1, stop2],
    )
    graph.add_line(line)
    graph.add_stop(stop3)  # Add stop3 without connecting it to the line
    return graph, stop1, stop2, stop3, line


def test_compute_distance_matrix():

    graph, stop1, stop2, stop3, line = generate_test_graph()

    # Compute distance matrix
    distance_matrix, path_matrix, stops_id_to_index = hbus.compute_distance_matrix(graph)

    # Check distances and paths
    assert stops_id_to_index == {0: stop1.id, 1: stop2.id, 2: stop3.id}

    assert distance_matrix[0, 1] - 111319.49079327357 < 1e-6
    assert distance_matrix[0, 2] == float("inf")
    assert distance_matrix[1, 2] == float("inf")

    assert path_matrix[0, 1] == [
        "0",
        "1",
    ]
    assert path_matrix[0, 2] is None
    assert path_matrix[1, 2] is None


def test_no_stops():
    graph = hbus.BusNetworkGraph()
    distance_matrix, path_matrix, stops_id_to_index = hbus.compute_distance_matrix(graph)
    assert distance_matrix.shape[0] == 0
