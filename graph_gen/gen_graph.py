import re

def transform_graph_spec(graph_spec: str) -> str:
    lines = graph_spec.split('\n')
    transformed_lines = []

    for line in lines:
        if '=>' in line and not line[0].isspace():
            parts = line.split('=>')
            if parts[0].strip():
                transformed_lines.append(parts[0].strip())
                transformed_lines.append(f"  => {parts[1].strip()}")
            else:
                transformed_lines.append(line)
        else:
            transformed_lines.append(line)

    return '\n'.join(transformed_lines)


def parse_string(input_string):
    pattern = r"\[(\w+)\((\w+) in (\w+)\)\]"
    match = re.match(pattern, input_string)
    
    if match:
        function, var_name, state_field = match.groups()
        return function, var_name, state_field
    else:
        raise ValueError("String format is incorrect")


def parse_graph_spec(graph_spec):
    graph_spec = transform_graph_spec(graph_spec)
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

def all_true_fn(edges):
    return all(edge['condition'] == 'true_fn' for edge in edges)

def mk_conditions(node_name, node_dict):
    edges = node_dict['edges']
    state_type = node_dict['state']

    # Special case: single 'true_fn' condition
    if  all_true_fn(edges):
        return ""

    function_body = [f"def after_{node_name}(state: {state_type}):"]

    for i, edge in enumerate(edges):
        condition = edge['condition']
        destination = edge['destination']
    
        if ',' in destination:
            # Split the destination by commas and strip spaces
            destinations = [d.strip() for d in destination.split(',')]
            # Format the return statement with a list
            return_statement = f"return {destinations}"
        else:
            # Format the return statement with a single value
            return_statement = f"return '{destination}'"
    
        if condition == 'true_fn':
            function_body.append(f"    {return_statement}")
            break  # Exit the loop as this is always true
        elif i == 0:
            function_body.append(f"    if {condition}(state):")
        else:
            function_body.append(f"    elif {condition}(state):")
    
        function_body.append(f"        {return_statement}")


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

    # Case 1: parallel output
    if all_true_fn(edges):
        edge_code = ""
        for edge in edges:
            destination = edge['destination']
            if destination == 'END':
                edge_code += f"{graph_name}.add_edge('{node_name}', END)\n"
            elif ',' in destination:
                data = destination.split(',')
                for x in data:
                    x = x.strip()
                    edge_code += f"{graph_name}.add_edge('{node_name}', '{x}')\n"
            elif '[' in destination:
                function, var_name, state_field = parse_string(destination)
                edge_code += f"def after_{node_name}(state):\n"
                edge_code += f"    return [Send('{function}', {{'{var_name}': s}}) for s in state['{state_field}']]\n"
                edge_code += f"{graph_name}.add_conditional_edges('{node_name}', after_{node_name}, ['{function}'])\n"
            else:
                edge_code += f"{graph_name}.add_edge('{node_name}', '{destination}')\n"
        return edge_code.rstrip()

    # Case 2: Multiple conditions
    else:
        # Helper function to create dictionary entries
        def maybe_multiple(s):
            if "," in s:
                data = s.split(',')
                quoted = [f"'{x.strip()}'" for x in data]
                return "[" + ','.join(quoted) + "]"
            else:
                return f"'{s}'"

        def mk_entry(edge):
            if edge['destination'] == 'END':
                return f"'{edge['destination']}': END"
            else:
                return f"'{edge['destination']}': {maybe_multiple(edge['destination'])}"

        # Create the dictionary string
        dict_entries = ', '.join([mk_entry(e) for e in edges])
        # If there's a single edge with a condition, dict needs END: END
        if len(edges) == 1 and edges[0]['condition'] != 'true_fn':
            dict_entries += ", END: END"
        node_dict_str = f"{node_name}_dict = {{{dict_entries}}}"
        multiple = any("," in edge['destination'] for edge in edges)
        if multiple:
            # not really understanding, but it seems that in this case, we just have a list of 
            # nodes instead of a dict for third parameter
            s = set()
            for edge in edges:
                destinations = edge['destination'].split(',')
                for dest in destinations:
                    s.add(dest.strip())
            node_dict_str = f"{node_name}_dict = {list(s)}"
            
        # Create the add_conditional_edges call
        add_edges_str = f"{graph_name}.add_conditional_edges('{node_name}', after_{node_name}, {node_name}_dict)"

        return f"{node_dict_str}\n{add_edges_str}\n"

def true_fn(state):
    return True

def gen_graph(graph_name, graph_spec, memory=None):
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
        conditions = mk_conditions(node_name, node_dict)
        if conditions: 
            node_code.append(conditions)
        conditional_edges = mk_conditional_edges(graph_name, node_name, node_dict)
        if conditional_edges:
            node_code.append(conditional_edges)
    mem_spec = ""
    if memory:
        mem_spec = f"checkpointer={memory}"
    return graph_setup + "\n".join(node_code) + "\n\n" + f"{graph_name} = {graph_name}.compile({mem_spec})"