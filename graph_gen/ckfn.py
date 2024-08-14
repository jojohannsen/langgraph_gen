from typing import TypedDict, get_origin, get_args, Union, Callable, Any, Tuple, Dict
import inspect

def is_typeddict(annotation):
    try:
        return issubclass(annotation, dict) and hasattr(annotation, '__annotations__')
    except TypeError:
        return hasattr(annotation, '__origin__') and issubclass(annotation.__origin__, dict) and hasattr(annotation, '__annotations__')

def check_return_type(return_annotation, expected_return_type):
    if return_annotation is inspect.Signature.empty:
        return False
    if expected_return_type is Any:
        return True
    if isinstance(expected_return_type, type):
        return issubclass(return_annotation, expected_return_type)
    return return_annotation == expected_return_type

def check_for_function(function_name: str, expected_return_type: Union[type, Any, None] = None) -> Tuple[bool, str]:
    namespace = dict(globals(), **locals())
    
    if function_name not in namespace:
        return False, f"Function '{function_name}' does not exist."
    
    func = namespace[function_name]
    
    if not callable(func):
        return False, f"'{function_name}' exists but is not a function."
    
    signature = inspect.signature(func)
    parameters = list(signature.parameters.values())
    
    if not parameters:
        return False, f"Function '{function_name}' exists but has no parameters."
    
    first_param = parameters[0]
    
    if first_param.annotation is inspect.Parameter.empty:
        return False, f"Function '{function_name}' exists but its first parameter has no type annotation."
    
    if not is_typeddict(first_param.annotation):
        return False, f"Function '{function_name}' exists but its first parameter is not a TypedDict."
    
    if expected_return_type is not None:
        return_annotation = signature.return_annotation
        if not check_return_type(return_annotation, expected_return_type):
            return False, f"Function '{function_name}' return type does not match the expected type."
    
    return True, f"Function '{function_name}' exists, its first parameter is a TypedDict, and its return type is correct (if specified)."

def generate_langgraph_code(node_dict: Dict[str, Any]):
    # Langgraph Nodes
    yield "# Langgraph Nodes"
    for node_name in node_dict:
        exists, message = check_for_function(node_name, Dict[str, Any])
        if exists:
            yield f"# '{node_name}' already exists"
        else:
            yield f"# '{node_name}' not found -- {message}"
    
    # Langgraph Conditional Edges
    yield "# Langgraph Conditional Edges"
    for node_name, node_data in node_dict.items():
        if 'edges' in node_data:
            for edge in node_data['edges']:
                condition = edge.get('condition')
                if condition and condition != 'true_fn':
                    exists, message = check_for_function(condition, bool)
                    if exists:
                        yield f"# Condition '{condition}' for node '{node_name}' already exists"
                    else:
                        yield f"# Condition '{condition}' for node '{node_name}' not found -- {message}"