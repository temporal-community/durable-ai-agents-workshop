# Sessions MCP Server

A small MCP server over a local conference schedule, used by modules 3 and 4.

Three tools: `list_sessions`, `get_session`, `search_speakers`. The data is `sessions.json`, ten
real talks from [PyCon AU 2026](https://2026.pycon.org.au/schedule/) in Brisbane. Swap that file
and the server is about a different conference.

It speaks stdio, so nothing runs until a worker launches it as a child process. To poke at it by
hand:

```bash
uv sync
uv run python -m server
```

Workers find it through `MCP_SERVER_HOME`, which defaults to this directory.
