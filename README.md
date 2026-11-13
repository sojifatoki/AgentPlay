# agentPlay

A small AI agent I wrote in plain Python. No LangChain, no agent framework, just a loop, a tool registry and one tool (web search).

I lead an engineering team and I come from test automation. I kept reading about agents and wanted to see what's actually going on inside one, so I built the smallest version I could and worked up from there. It's a learning project, not production code.

## What it does

You type a question. The agent sends it to the model along with a list of tools it's allowed to use. If the model wants current information it asks for a search, the loop runs the search and hands the results back, and the model tries again. It stops when the model answers without asking for a tool, or after 5 steps, whichever comes first.

There's one tool right now, `search_web`, built on Tavily. It takes a query and optionally a topic (general, news or finance), a time range, a country and a max number of results.

## What's in the repo

- `simple_agent_loop.py` is the loop. `run_agent(question)` is the whole agent.
- `tool_registry.py` has the `@tool` decorator. It also builds the tool definitions the model reads from each function's signature and docstring, and runs a tool by name when the model asks.
- `tools.py` is where tools live. Only `search_web` for now.

## Adding a tool

Write a function with type hints and a docstring, then put `@tool` on it in `tools.py`:

```python
@tool
def get_word_count(text: str) -> int:
    """Count the words in a piece of text."""
    return len(text.split())
```

The docstring is what the model reads to decide when to call it, so write it for the model, not for me.

## Running it

You need Python 3.14 and [uv](https://github.com/astral-sh/uv).

```
git clone <your-repo-url>
cd agentPlay
uv sync
```

Make a `.env` file with your keys:

```
OPENAI_API_KEY=...
TAVILY_API_KEY=...
ANTHROPIC_API_KEY=""
GEMINI_API_KEY=""
MODEL=openai/gpt-4o-mini
```

There's a `.env.template` you can copy. `MODEL` is optional and defaults to `openai/gpt-4o-mini`.

Then:

```
uv run simple_agent_loop.py
```

It'll prompt you for a question. The model is set by `MODEL` in your `.env` file. Calls go through litellm, so switching providers is just a new model string (for example `MODEL=anthropic/claude-sonnet-5-5`) plus the matching API key (for example `ANTHROPIC_API_KEY`) in `.env`. I've tested this by switching between providers and it works without any code changes.

## Lessons learned

The model only knows what the tool definition tells it. My registry builds that definition from type hints, and anything it doesn't recognize falls back to a plain string. That includes `Literal` and `str | None`. So the model is never told that `topic` has to be general, news or finance. It could send something else and Tavily would reject it. I haven't seen that happen, but nothing stops it. Mapping `Literal` to an enum is the fix.

Errors go back to the model as text. Both `search_web` and `run_tool` catch exceptions and return a string instead of crashing, so the model can see what went wrong and try again or explain it. The downside is that a failed search can read like a normal result if the model glosses over it.

You need a step limit. Mine is `MAX_STEPS = 5`, which is a guess. Without it a confused model can keep calling tools forever. When the limit is hit the function returns "Stopped: reached the step limit" so there's an answer of some kind, but it's not a good one.

Import order matters. Tools register themselves when `tools.py` is imported, so `import tools` has to come before `get_tool_definitions()`. Get it backwards and the model gets an empty tool list. That's why there's a comment about it at the top of the loop file.

The whole conversation goes back to the model on every step, and search results are long. Each pass through the loop adds the full search results, as JSON, to the history, so a five-step run costs a lot more than five times a one-step run. I want to trim or summarize results before they go back in.

Writing the loop myself took the mystery out of it. A tool result is just another message with a `tool` role, tied to the request by an id. The loop is under 50 lines, comments included. Most of the real work is in the edges: schemas, errors, limits.

## What's next

- An eval set, so the Results table above stops saying TBD
- Logging for each step, plus token counts and run-time per question
- Trimming search results before they go back into the conversation
- More tools, most likely reading files and running tests
- Memory between questions. Right now every run starts from scratch.
- Multi-agent system - will most likely create this in another repo
