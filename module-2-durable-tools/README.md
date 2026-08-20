# Module 2: Durable Tools

The module 1 agent, now with tools. Each tool is a Temporal activity, so each tool call gets its own
retry policy and its own entry in event history.

## What's different from module 1

`tool_activities.py` is new. Four `@activity.defn` functions call public HTTP APIs. The agent gets
them through `activity_as_tool(...)`, and the worker registers them in `activities=[...]`.

The Agents SDK builds each tool's schema from the function signature and its docstring, so the
docstrings are part of the contract. Write them for the model.

## Architecture

- `activity_as_tool(get_weather, start_to_close_timeout=...)` presents a Temporal activity to the
  SDK as a tool. Every call the model makes becomes a scheduled activity.
- The worker must register the same functions in `activities=[...]`, or the activity has nowhere
  to run.

### Trade-off

Tools are now `@activity.defn` functions. They gain retries, timeouts and history for free, and they
stop being plain Python: they only run under a Temporal worker.

### Tools

| Tool | API | Purpose |
|------|-----|---------|
| `get_ip_address` | icanhazip.com | The caller's public IP |
| `get_location_info` | ip-api.com | City, country, lat/lon for an IP |
| `get_coordinates` | Open-Meteo Geocoding | lat/lon for a city name |
| `get_weather` | Open-Meteo Forecast | Current temperature, weather code, wind speed |

None of them need an API key.

## What to notice

Event history now shows the agentic loop written out: a model activity, then a tool activity, then
another model activity, until the model stops asking for tools. The same shape appears in the OpenAI
trace. Nobody wrote that loop. `Runner.run` owns it, and Temporal recorded every step.

## Prerequisites

Same as module 1.

## Run it

```bash
cd exercise && uv sync
```

Two `TODO`s, one in `worker.py` and one in `agent_workflow.py`. Then:

```bash
uv run python -m worker
uv run python -m start_workflow "What is the weather where I am right now?"
```

Task queue: `durable-tools-tq`.
