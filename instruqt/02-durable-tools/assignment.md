---
slug: durable-tools
id: ""
type: challenge
title: "Module 2: Durable Tools"
teaser: Tools become Temporal activities. Every tool call gets a retry policy and a history entry.
notes:
- type: text
  contents: |-
    # The agent just made something up

    In module 1 it answered a weather question with no weather data. Models do
    that. The fix is tools.

    A tool is a network call, which means a tool is a thing that fails. Where
    does the loop stand when the third of five tool calls times out?
- type: text
  contents: |-
    # The trade

    Tools become @activity.defn functions. Each call gets retries, a timeout,
    and its own line in event history.

    They also stop being plain Python. They only run under a worker now.
tabs:
- title: Worker
  type: terminal
  hostname: workshop
  workdir: /root/workshop/module-2-durable-tools/exercise
- title: Starter
  type: terminal
  hostname: workshop
  workdir: /root/workshop/module-2-durable-tools/exercise
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
  path: /root/workshop/module-2-durable-tools/exercise
- title: Solution
  type: code
  hostname: workshop
  path: /root/workshop/module-2-durable-tools/solution
difficulty: basic
timelimit: 1800
---

# Durable Tools

Four tools, four public APIs, no API keys. Each one becomes an activity.

> [!NOTE]
> **Your tabs.**
> - [button label="Worker" background="#444CE7"](tab-0) runs the worker.
> - [button label="Starter" background="#444CE7"](tab-1) launches workflows.
> - [button label="Temporal UI" background="#444CE7"](tab-2) is the event history.
> - [button label="Network Control Panel" background="#444CE7"](tab-3) turns external services off.
> - [button label="Editor" background="#444CE7"](tab-4) is your working copy.
> - [button label="Solution" background="#444CE7"](tab-5) is the finished code.

## What Changed

`tool_activities.py` is new: four `@activity.defn` functions hitting icanhazip, ip-api and
Open-Meteo. Two other things moved:

- `agent_workflow.py` wraps each one in `activity_as_tool(...)` and passes them as `tools=[...]`.
- `worker.py` has to register the same functions in `activities=[...]`, or the activity has nowhere
  to run.

The Agents SDK builds each tool's schema from the signature and the docstring. Read one of those
docstrings. It is written for the model, not for you.

## Wire Up the Tools

Two `TODO`s in the [button label="Editor" background="#444CE7"](tab-4) tab, one in `worker.py` and
one in `agent_workflow.py`.

## Start the Worker

Click the [button label="Worker" background="#444CE7"](tab-0) terminal.

```bash,run
uv run python -m worker
```

## Run It

Click the [button label="Starter" background="#444CE7"](tab-1) terminal. This question needs three
tools chained, so the model has to work for it.

```bash,run
uv run python -m start_workflow "Where am I, and what is the weather there?"
```

## Watch the Event History

Click the [button label="Temporal UI" background="#444CE7"](tab-2) tab and open your workflow.

The loop is written out in front of you. A model activity, then a tool activity, then another model
activity, until the model stops asking. Nobody wrote that loop. `Runner.run` owns it and Temporal
recorded every step of it.

The same shape shows up at https://platform.openai.com/traces, from the agent's side.

## Break It

Click the [button label="Network Control Panel" background="#444CE7"](tab-3) tab and toggle
**Weather** off, leaving **OpenAI** on. Run the workflow again.

In the [button label="Temporal UI" background="#444CE7"](tab-2) tab: `get_weather` is **Retrying**,
and every model activity and tool call before it is still **Completed**.

> The failure is downstream of work you already paid for. What happens to that work?

<details>
<summary>Answer</summary>

Nothing. It stays in event history. When `get_weather` finally succeeds, the loop continues from
that point with the earlier results intact. It does not re-ask the model and it does not re-call the
tools that already returned.
</details>

Toggle **Weather** back on and let it finish.

## Summary

| | Tool as a plain function | Tool as an activity |
|---|---|---|
| Retry on failure | Your `try`/`except` | Retry policy |
| Visible in history | No | One entry per call |
| Timeout | Whatever the client does | `start_to_close_timeout` |
| Runs anywhere | Yes | Needs a worker |
