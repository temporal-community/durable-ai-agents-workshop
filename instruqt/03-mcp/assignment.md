---
slug: mcp
id: ""
type: challenge
title: "Module 3: MCP"
teaser: A second source of tools. Each MCP call becomes its own Temporal activity.
notes:
- type: text
  contents: |-
    # Someone else's tools

    You will not write every tool your agent needs. MCP is how you borrow the
    ones somebody else already built.

    The server in this module is 50 lines over a JSON file. Read all of it.
- type: text
  contents: |-
    # The trade

    MCP tools now run as activities too, so they are coupled to Temporal the
    same way your own tools are.

    What that buys is a retry policy and a history entry per MCP call, instead
    of an opaque call somewhere inside the agent loop.
tabs:
- title: Worker
  type: terminal
  hostname: workshop
  workdir: /root/workshop/module-3-mcp/exercise
- title: Starter
  type: terminal
  hostname: workshop
  workdir: /root/workshop/module-3-mcp/exercise
- title: Temporal UI
  type: service
  hostname: workshop
  port: 8233
  path: /
- title: Network Control Panel
  type: service
  hostname: workshop
  port: 5000
  path: /
- title: Editor
  type: code
  hostname: workshop
  path: /root/workshop/module-3-mcp/exercise
- title: Solution
  type: code
  hostname: workshop
  path: /root/workshop/module-3-mcp/solution
difficulty: basic
timelimit: 1800
---

# MCP

Conference data over MCP, weather over activities, both durable, one agent.

> [!NOTE]
> **Your tabs.**
> - [button label="Worker" background="#444CE7"](tab-0) runs the worker.
> - [button label="Starter" background="#444CE7"](tab-1) launches workflows.
> - [button label="Temporal UI" background="#444CE7"](tab-2) is the event history.
> - [button label="Network Control Panel" background="#444CE7"](tab-3) turns external services off.
> - [button label="Editor" background="#444CE7"](tab-4) is your working copy.
> - [button label="Solution" background="#444CE7"](tab-5) is the finished code.

## What Changed

The server lives at `/root/workshop/mcp-server/server.py`. Three tools over `sessions.json`:
`list_sessions`, `get_session`, `search_speakers`. Nothing to install, nothing to clone.

Two pieces connect it:

- `worker.py` registers it with `StatelessMCPServerProvider(name="sessions", server_factory=...)`.
  The factory returns an `MCPServerStdio`, so the worker launches the server as a child process and
  speaks JSON-RPC over its stdin and stdout. No port, no service to keep alive.
- `agent_workflow.py` takes the workflow-side handle from `stateless_mcp_server("sessions")` and
  hands it to the agent as `mcp_servers=[...]`.

Each `listTools` and each `callTool` becomes a Temporal activity that connects, calls, and cleans up.

## Wire Up the MCP Server

Two `TODO`s in the [button label="Editor" background="#444CE7"](tab-4) tab, one per file.

## Start the Worker

Click the [button label="Worker" background="#444CE7"](tab-0) terminal.

```bash,run
uv run python -m worker
```

## Run It

Click the [button label="Starter" background="#444CE7"](tab-1) terminal. This question needs both
sides: the schedule from MCP, the forecast from an activity.

```bash,run
uv run python -m start_workflow "Which AI track sessions are on Saturday, and what is the weather in Melbourne?"
```

## Watch the Event History

Click the [button label="Temporal UI" background="#444CE7"](tab-2) tab and open your workflow.

Two new activity names sit alongside the weather ones:

```text,nocopy
sessions-stateless-list-tools
sessions-stateless-call-tool-v2
```

The first one runs before the model has said anything. The agent cannot choose a tool it has not
been told about, so listing the tools is itself a durable step.

## Break It

Click the [button label="Network Control Panel" background="#444CE7"](tab-3) tab, toggle **OpenAI**
off, and run the workflow again.

> The MCP server is a local child process. Does it care that the network is gone?

<details>
<summary>Answer</summary>

No. `sessions-stateless-list-tools` completes normally while the model activity retries. Look at the
history and you can see exactly which parts of the agent depend on the network and which do not.
That is the useful thing about every step being an activity.
</details>

Toggle **OpenAI** back on and let it finish.

## Summary

| | Calling MCP from the agent directly | MCP through the provider |
|---|---|---|
| Retry on a failed tool call | The SDK's, if any | Activity retry policy |
| Visible in history | No | One entry per MCP operation |
| Connection lifetime | Held by the agent | One activity, then closed |
| Server process | Yours to manage | Launched per call by the worker |
