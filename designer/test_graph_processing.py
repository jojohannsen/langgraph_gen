import pytest
from graph_processing import process_events, GraphContext, GraphSpec, GraphNode, GraphEdge
from spec_to_events import NodeEvent, UnconditionalEdge, ConditionalEdge

def test_process_events():
    events = [
        NodeEvent("node1"),
        UnconditionalEdge("node2"),
        NodeEvent("node2"),
        ConditionalEdge("condition_x", "node3"),
        NodeEvent("node3"),
    ]

    context, graph_spec = process_events(events)

    # Check final state
    assert set(context.map_node_name.keys()) == {"node1", "node2", "node3"}
    assert context.current_node_name == "node3"

    # Check node1
    assert len(context.map_node_name["node1"].outgoing_edges) == 1
    assert context.map_node_name["node1"].outgoing_edges[0].dest_node == "node2"
    assert context.map_node_name["node1"].outgoing_edges[0].condition is None

    # Check node2
    assert len(context.map_node_name["node2"].outgoing_edges) == 1
    assert context.map_node_name["node2"].outgoing_edges[0].dest_node == "node3"
    assert context.map_node_name["node2"].outgoing_edges[0].condition == "condition_x"

    # Check node3
    assert len(context.map_node_name["node3"].outgoing_edges) == 0

    # Check node codes
    for node_name in ["node1", "node2", "node3"]:
        assert context.map_node_name[node_name].node_code == f"def {node_name}(state):\n    pass\n"

    # Check final state of graph_spec
    assert len(graph_spec.nodes) == 3
    assert [node.node_code for node in graph_spec.nodes] == [
        "def node1(state):\n    pass\n",
        "def node2(state):\n    pass\n",
        "def node3(state):\n    pass\n"
    ]

def test_process_events_with_duplicate_nodes():
    events = [
        NodeEvent("node1"),
        UnconditionalEdge("node2"),
        NodeEvent("node1"),  # Duplicate node
        ConditionalEdge("condition_x", "node3"),
    ]

    context, graph_spec = process_events(events)

    # Check that node1 was not duplicated
    assert len(context.map_node_name) == 1
    assert len(graph_spec.nodes) == 1

    # Check that both edges were added to node1
    assert len(context.map_node_name["node1"].outgoing_edges) == 2
    assert context.map_node_name["node1"].outgoing_edges[0].dest_node == "node2"
    assert context.map_node_name["node1"].outgoing_edges[0].condition is None
    assert context.map_node_name["node1"].outgoing_edges[1].dest_node == "node3"
    assert context.map_node_name["node1"].outgoing_edges[1].condition == "condition_x"

def test_process_events_with_missing_node_for_edge():
    events = [
        UnconditionalEdge("node2"),  # Edge without a preceding node
    ]

    context, graph_spec = process_events(events)

    # Check that no nodes or edges were created
    assert len(context.map_node_name) == 0
    assert len(graph_spec.nodes) == 0

if __name__ == "__main__":
    pytest.main([__file__])