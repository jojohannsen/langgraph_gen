def parse_graph_spec(graph_spec):
    TRUE_FN = 'true_fn'
    graph = {}
    current_node = None
    state = None
    start_node = None

    for line in graph_spec.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if '=>' in line:
            if line.startswith('=>'):
                condition = TRUE_FN
                destination = line.split('=>')[1].strip()
                graph[current_node]['edges'].append({'condition': condition, 'destination': destination})
            else:
                parts = line.split('=>')
                condition = parts[0].strip()
                destination = parts[1].strip()
                graph[current_node]['edges'].append({'condition': condition, 'destination': destination})
        elif '(' in line:
            node_info = line.split('(')
            current_node = node_info[0].strip()
            start_node = current_node
            state = node_info[1].strip(')')
            graph[current_node] = {'state': state, 'edges': []}
        else:
            current_node = line
            graph[current_node] = {'state': state, 'edges': []}
    return graph, start_node


def mk_conditions(node_name, node_dict):
    edges = node_dict['edges']
    state_type = node_dict['state']

    # Special case: single 'true_fn' condition
    if len(edges) == 1 and edges[0]['condition'] == 'true_fn':
        return ""

    function_body = [f"def after_{node_name}(state: {state_type}):"]

    for i, edge in enumerate(edges):
        condition = edge['condition']
        destination = edge['destination']

        if condition == 'true_fn':
            function_body.append(f"    return '{destination}'")
            break  # Exit the loop as this is always true
        elif i == 0:
            function_body.append(f"    if {condition}(state):")
        else:
            function_body.append(f"    elif {condition}(state):")

        function_body.append(f"        return '{destination}'")

    # Only add the else clause if we didn't encounter 'true_fn'
    if condition != 'true_fn':
        if len(edges) > 1:
            function_body.append("    else:")
            function_body.append("        raise ValueError(\"No destination\")")
        else:
            function_body.append("    return END")
    function_body.append("")

    return "\n".join(function_body)

def mk_conditional_edges(graph_name, node_name, node_dict):
    edges = node_dict['edges']

    # Case 1: Single 'true_fn' condition
    if len(edges) == 1 and edges[0]['condition'] == 'true_fn':
        destination = edges[0]['destination']
        if destination == 'END':
            return f"{graph_name}.add_edge('{node_name}', END)"
        else:
            return f"{graph_name}.add_edge('{node_name}', '{destination}')"

    # Case 2: Multiple conditions
    else:
        # Helper function to create dictionary entries
        def mk_entry(edge):
            if edge['destination'] == 'END':
                return f"'{edge['destination']}': END"
            else:
                return f"'{edge['destination']}': '{edge['destination']}'"

        # Create the dictionary string
        dict_entries = ', '.join([mk_entry(e) for e in edges])
        # If there's a single edge with a condition, dict needs END: END
        if len(edges) == 1 and edges[0]['condition'] != 'true_fn':
            dict_entries += ", END: END"
        node_dict_str = f"{node_name}_dict = {{{dict_entries}}}"

        # Create the add_conditional_edges call
        add_edges_str = f"{graph_name}.add_conditional_edges('{node_name}', after_{node_name}, {node_name}_dict)"

        return f"{node_dict_str}\n{add_edges_str}\n"

def true_fn(state):
    return True

def gen_graph(graph_name, graph_spec):
    graph, start_node = parse_graph_spec(graph_spec)

    # Generate the graph state, node definitions, and entry point
    graph_setup = f"{graph_name} = StateGraph({graph[start_node]['state']})\n"
    if graph[start_node]['state'] == 'MessageGraph':
        graph_setup = f"{graph_name} = MessageGraph()\n"
    for node_name in graph:
        graph_setup += f"{graph_name}.add_node('{node_name}', {node_name})\n"
    graph_setup += f"\n{graph_name}.set_entry_point('{start_node}')\n\n"

    # Generate the code for edges and conditional edges
    node_code = []
    for node_name, node_dict in graph.items():
        node_code.append(mk_conditions(node_name, node_dict))
        node_code.append(mk_conditional_edges(graph_name, node_name, node_dict))

    return graph_setup + "\n".join(node_code) + "\n\n" + f"\n\n{graph_name} = {graph_name}.compile()"