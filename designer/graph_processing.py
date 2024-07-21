from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class StateField(BaseModel):
    field_name: str
    data_type: str
    reducer: Optional[str] = None

class StateSpec(BaseModel):
    name: str
    fields: List[StateField]

class GraphEdge(BaseModel):
    condition: Optional[str] = None
    dest_node: str

class GraphNode(BaseModel):
    run_outgoing_edges_in_parallel: bool = False
    outgoing_edges: List[GraphEdge] = Field(default_factory=list)
    is_start_node: bool = False
    node_code: str = ""

class GraphSpec(BaseModel):
    spec_text: str
    nodes: List[GraphNode] = Field(default_factory=list)
    memory: Optional[str] = None

class GraphContext(BaseModel):
    map_node_name: Dict[str, GraphNode] = Field(default_factory=dict)
    current_node_name: Optional[str] = None
    state_spec: StateSpec = Field(default_factory=lambda: StateSpec(name="State", fields=[]))

def process_events(events):
    context = GraphContext()
    graph_spec = GraphSpec(spec_text="")

    node_code_template = "def {node_name}({state_name}):\n    pass\n"

    for event in events:
        if isinstance(event, NodeEvent):
            node_name = event.name
            context.current_node_name = node_name
            if node_name not in context.map_node_name:
                new_node = GraphNode(
                    node_code=node_code_template.format(
                        node_name=node_name,
                        state_name=context.state_spec.name.lower()
                    )
                )
                context.map_node_name[node_name] = new_node
                graph_spec.nodes.append(new_node)

        elif isinstance(event, UnconditionalEdge):
            if context.current_node_name:
                current_node = context.map_node_name[context.current_node_name]
                current_node.outgoing_edges.append(GraphEdge(dest_node=event.dest_node))

        elif isinstance(event, ConditionalEdge):
            if context.current_node_name:
                current_node = context.map_node_name[context.current_node_name]
                current_node.outgoing_edges.append(GraphEdge(condition=event.condition, dest_node=event.dest_node))

    return context, graph_spec

# Import the event classes from spec_to_events.py
from spec_to_events import NodeEvent, UnconditionalEdge, ConditionalEdge

# Explicitly export the classes and function
__all__ = ['StateField', 'StateSpec', 'GraphEdge', 'GraphNode', 'GraphSpec', 'GraphContext', 'process_events']
