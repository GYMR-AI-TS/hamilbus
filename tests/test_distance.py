import hamilbus as hbus


def generate_test_graph():
    graph = hbus.BusNetworkGraph()
    stop1 = hbus.Stop(
        index=0,
        name="Stop 1",
        type="parent_station",
        lat=0,
        lon=0,
    )
    stop2 = hbus.Stop(
        index=1,
        name="Stop 2",
        type="parent_station",
        lat=0,
        lon=1,
    )
    stop3 = hbus.Stop(
        index=2,
        name="Stop 3",
        type="parent_station",
        lat=1,
        lon=0,
    )
    line = hbus.Line(
        index=0,
        name="Line 1",
        long_name="Line 1",
        color="#93A14E",
        shape=[(0, 0), (0, 1)],
        stops=[stop1, stop2],
    )
    graph.add_line(line)
    graph.add_stop(stop3)  # Add stop3 without connecting it to the line
    return graph, stop1, stop2, stop3, line


def test_compute_distance_matrix():

    graph, stop1, stop2, stop3, line = generate_test_graph()

    # Compute distance matrix
    distance_matrix = hbus.compute_distance_matrix(graph)

    # Check distances and paths
    assert (stop1.index, stop2.index) in distance_matrix
    assert (stop1.index, stop3.index) in distance_matrix
    assert (stop2.index, stop3.index) in distance_matrix

    assert (
        distance_matrix[(stop1.index, stop2.index)]["distance"] - 111319.49079327357
        < 1e-6
    )
    assert distance_matrix[(stop1.index, stop3.index)]["distance"] == float("inf")
    assert distance_matrix[(stop2.index, stop3.index)]["distance"] == float("inf")

    assert distance_matrix[(stop1.index, stop2.index)]["path"] == [
        stop1.index,
        stop2.index,
    ]
    assert distance_matrix[(stop1.index, stop3.index)]["path"] == []
    assert distance_matrix[(stop2.index, stop3.index)]["path"] == []


def test_no_stops():
    graph = hbus.BusNetworkGraph()
    distance_matrix = hbus.compute_distance_matrix(graph)
    assert distance_matrix == {}
