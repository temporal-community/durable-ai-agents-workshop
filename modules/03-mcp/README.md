# Module 3: MCP

The agent gains a second source of tools: an MCP server. Weather still comes from Temporal
activities, conference data comes over MCP, and both are durable.

## What's different from module 2

The worker registers an MCP server with `StatelessMCPServerProvider`, and the workflow hands it to
the agent with `mcp_servers=[...]`. Nothing else about the agent changes.

The server is `../mcp-server/server.py` in this repo: about 50 lines of FastMCP over a JSON file
of conference sessions. Read the whole thing. There is nothing to install and nothing to clone.

## Architecture

- `MCPServerStdio` is the Agents SDK's stdio transport. The worker launches the server as a child
  process and speaks JSON-RPC over its stdin and stdout. No port, no service to keep running.
- `StatelessMCPServerProvider(name="sessions", server_factory=...)` registers it on the worker under
  a name. Each `listTools` and `callTool` becomes its own Temporal activity, which connects, calls,
  and cleans up.
- `stateless_mcp_server("sessions")` is the workflow-side handle passed to `Agent(mcp_servers=[...])`.

`MCP_SERVER_HOME` points at the server directory. It defaults to `modules/mcp-server/` relative to
each module, so you only set it if you move things. In the Instruqt sandbox it has its own Editor
tab, since it is not just a black box the workflow calls: you can read and change it too.

### Trade-off

MCP tools and activity tools are now both coupled to Temporal, because both run as activities. What
you get for that is a retry policy and a history entry per MCP call, instead of an opaque call
inside the agent loop.

### Tools

| Tool | Source | Purpose |
|------|--------|---------|
| `list_sessions` | MCP | Sessions, filtered by day or track |
| `get_session` | MCP | One session by id |
| `search_speakers` | MCP | Sessions matching a speaker name |
| `get_coordinates`, `get_weather`, ... | Activities | Unchanged from module 2 |

## What to notice

Event history gains `sessions-stateless-list-tools` and `sessions-stateless-call-tool-v2` activities next to the weather
ones. Ask a question that needs both sides and watch the model chain them.

## Prerequisites

Same as module 1. No Node, no extra server to install.

## Run it

```bash
cd exercise && uv sync
```

Two `TODO`s, one in `worker.py` and one in `agent_workflow.py`. Then:

```bash
uv run python -m worker
uv run python -m start_workflow "Which Data & AI sessions are on Thursday, and what is the weather in Brisbane?"
```

Task queue: `mcp-agent-tq`.
