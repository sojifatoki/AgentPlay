import tools # This must come before get_tool_definitions(): running tools.py fills TOOLS
from typing import Any

from litellm import completion, ModelResponse


from tool_registry import get_tool_definitions, run_tool #This has to happen after importing tools



#send tool definitions to the LLM
MODEL = "gpt-4o-mini" 
MAX_STEPS = 5 #Limits the number of times the loop can run
SYSTEM_PROMPT = "Assume the role of a helpful assistant. You have access to tools when you need current information."

# messages = [
#     {"role": "system", "content":SYSTEM_PROMPT},
#     {"role": "user", "content": "Which AI model escaped its sandbox this week"}
# ]

def run_agent(question: str) -> str:
    """Answer the user's question with access to tools to do this."""
    
    #Start a conversation: SYSTEM_PROMPT + user's question
    messages: list[Any] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    #Generate tool schema/tool definition for available tool to pass to the LLM
    tool_definitions = get_tool_definitions()

    step = 1
    while step <= MAX_STEPS:
        #Send the entire conversation + tool list to the LLM
        response = completion(model=MODEL, 
                      messages=messages,
                      tools=tool_definitions)

        if not isinstance(response, ModelResponse):
            raise TypeError(f"Expected a ModelResponse, got {type(response).__name__}")

        reply = response.choices[0].message

        #Add the LLM's reply to the conversation history
        messages.append(reply)

        #Final stop if no tool use request by LLM
        if not reply.tool_calls:
            return reply.content or ""
        
        #Loop through and run all tools requested by the LLM
        for tool_call in reply.tool_calls:
            tool_name = tool_call.function.name
            if tool_name is None:
                tool_result = "Error: tool call had no function name"
            else:
                tool_arguments = tool_call.function.arguments
                print(f"Step {step}: calling {tool_name} with {tool_arguments}")
                tool_result = run_tool(tool_name, tool_arguments)

            tool_message = {
                "role":"tool",
                "tool_call_id": tool_call.id, #Link the call back to the LLM's request
                "content": tool_result
            }
            messages.append(tool_message)
       
        step = step + 1
    
    return "Stopped: reached the step limit without a final answer"

if __name__ == "__main__":
    question = input("What is your web search based query:  wh")
    #answer = run_agent("What's the latest instance of AI agents escaping their sandbox")
    answer = run_agent(question.strip())
    print(answer)
