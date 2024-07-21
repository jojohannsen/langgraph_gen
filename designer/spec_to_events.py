from dataclasses import dataclass

@dataclass
class NodeEvent:
    name: str

@dataclass
class UnconditionalEdge:
    dest_node: str

@dataclass
class ConditionalEdge:
    condition: str
    dest_node: str

def parse_graph_spec(graph_spec):
    lines = graph_spec.strip().split('\n')
    current_node = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if not line.startswith(' ') and '=>' not in line:
            current_node = line
            yield NodeEvent(current_node)
        else:
            parts = line.split('=>')
            if len(parts) == 1:
                # This is an unconditional edge without the '=>' symbol
                yield UnconditionalEdge(parts[0].strip())
            else:
                condition, dest_node = map(str.strip, parts)
                if condition:
                    yield ConditionalEdge(condition, dest_node)
                else:
                    yield UnconditionalEdge(dest_node)
