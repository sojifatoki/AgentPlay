import inspect

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