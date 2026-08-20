# Durable AI Agents: Modules

A 2-hour path from a bare agent to one that survives an outage, built with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and [Temporal](https://temporal.io/).
Four modules, each adding one thing:

1. `module-1-durable-agent` - an agent inside a Temporal workflow
2. `module-2-durable-tools` - tools as Temporal activities
3. `module-3-mcp` - a local MCP server alongside the activity tools
4. `module-4-failure` - the same agent, put under three kinds of failure

Every module has a `README.md`, an `exercise/` with `TODO`s to fill in, and a finished `solution/`.
This is the local path. The same four modules also run as an Instruqt track; see the root
`README.md` for that.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [Temporal CLI](https://docs.temporal.io/cli)
- An `OPENAI_API_KEY`

## Run it

Start the dev server once, in its own terminal:

```bash
temporal server start-dev
```

Then, for each module in order:

```bash
export OPENAI_API_KEY=...
cd module-N-*/exercise
uv sync
```

Fill in the module's `TODO`s, then:

```bash
uv run python -m worker            # stays running
uv run python -m start_workflow "your question"   # in another terminal
```

Watch the run in the Temporal Web UI at http://localhost:8233.

Module 3 onward needs `mcp-server/` (this repo's small FastMCP server over a conference schedule).
It is located via `MCP_SERVER_HOME`, which defaults to `../../mcp-server` relative to each module.
Set it explicitly if you move things:

```bash
export MCP_SERVER_HOME=/path/to/mcp-server
```

Module 4's failure lab uses no extra infrastructure. To take the network away, point
`OPENAI_BASE_URL` at a dead port instead of running the worker normally:

```bash
OPENAI_BASE_URL=http://127.0.0.1:1 uv run python -m worker
```

To kill the worker mid-run:

```bash
pkill -9 -f "module-4-failure"
```

Each module is independent: its own `pyproject.toml`, its own `uv.lock`, its own task queue. There
is nothing shared at the repo root beyond `mcp-server/`.
