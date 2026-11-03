import inspect
import json

TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}

TOOLS = {} #names of python functions

def tool(func):
    """Put @tool above any function to register it as an LLM tool."""
    TOOLS[func.__name__] = func
    return func

def make_tool_definition(func) -> dict:
    sig = inspect.signature(func)
    properties = {}
    required = []

    for name, param in sig.parameters.items():
        properties[name] = {"type": TYPE_MAP.get(param.annotation, "string")}
        if param.default is inspect.Parameter.empty: #no default -> required
            required.append(name)

    return {
        "type": "function",
        "function":{
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
                },
        },
    }

def get_tool_definitions() -> list:
    """Turn every @tool function into a definition the LLM can read."""
    return [make_tool_definition(func) for func in TOOLS.values()]

def run_tool(name: str, arguments_json: str) -> str | None:
    """LLM will locate a registered tool by name and call it with its provided argument."""
    func = TOOLS.get(name)

    if func is None:
        return f"Error: unknown tool '{name}'"
  
    try:
        args = json.loads(arguments_json or "{}") 
        result = func(**args) #unpack argument list in function call, same as search_web(query="...")
    except Exception as e:
        return f"Could not call function '{name}': {e} observed"
    
    #The LLM only accepts text, so have to convert lists/dicts result to a JSON string
    if isinstance(result, str):
        return result
    else:
        return json.dumps(result)
  