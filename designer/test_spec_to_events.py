import pytest
from spec_to_events import parse_graph_spec, NodeEvent, UnconditionalEdge, ConditionalEdge

def test_parse_graph_spec():
    graph_spec = """
    node_name_1
      => dest_node_A

    node_name_2
      condition_X => dest_node_B
      condition_Y => dest_node_C
    """

    events = list(parse_graph_spec(graph_spec))

    assert events == [
        NodeEvent("node_name_1"),
        UnconditionalEdge("dest_node_A"),
        NodeEvent("node_name_2"),
        ConditionalEdge("condition_X", "dest_node_B"),
        ConditionalEdge("condition_Y", "dest_node_C")
    ]

def test_parse_graph_spec_with_empty_lines():
    graph_spec = """
    node_name_1

    => dest_node_A

    node_name_2
      condition_X => dest_node_B

      condition_Y => dest_node_C
    """

    events = list(parse_graph_spec(graph_spec))

    assert events == [
        NodeEvent("node_name_1"),
        UnconditionalEdge("dest_node_A"),
        NodeEvent("node_name_2"),
        ConditionalEdge("condition_X", "dest_node_B"),
        ConditionalEdge("condition_Y", "dest_node_C")
    ]

def test_parse_graph_spec_with_unconditional_edge():
    graph_spec = """
    node_name_1
      => dest_node_A
    node_name_2
      => dest_node_B
    """

    events = list(parse_graph_spec(graph_spec))

    assert events == [
        NodeEvent("node_name_1"),
        UnconditionalEdge("dest_node_A"),
        NodeEvent("node_name_2"),
        UnconditionalEdge("dest_node_B")
    ]
