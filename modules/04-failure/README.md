# Module 4: Break It

The module 3 agent, put under three kinds of failure. The workflow gains one addition, a 10-second
pause before the agent starts, so the worker-kill demo has a reliable window instead of racing an
LLM response. This module is mostly running and watching; the one TODO teaches the judgement call
Temporal cannot make for you.

## 1. The network goes away

In the Instruqt sandbox, open the Network Control Panel and toggle **openai** off, then start a
workflow.

The Temporal UI shows the model activity as **Retrying**, not Failed. Attempts climb, the backoff
grows, and every tool call and MCP result that already completed is still sitting in event history.
Toggle **openai** back on. The next attempt succeeds and the same workflow execution finishes.

Nothing restarted. The client was never involved. You wrote no retry loop.

Running locally instead? Point the agent at a dead port:

```bash
OPENAI_BASE_URL=http://127.0.0.1:1 uv run python -m worker
```

## 2. The worker dies

Start a workflow, then immediately kill the worker hard:

```bash
pkill -9 -f "04-failure"
```

`-9` matters. A polite `SIGTERM` lets the SDK drain whatever it is holding, which is not the failure
you want to demonstrate. You have 10 seconds before the agent makes its first call, that pause is a
`workflow.sleep(...)`, itself a durable timer, not a trick. Restart the worker. The same workflow,
the same run id, picks up where it stopped, because the loop's state lives in event history and not
in that process.

## 3. Failures that should not be retried

Not every failure deserves a retry. A 503 from an overloaded API will pass on the next attempt. A
400 will fail identically forever, and Temporal will keep paying for attempts until a timeout.

That is the `TODO` in `tool_activities.py`: raise `ApplicationError(..., non_retryable=True)` for
4xx responses and let everything else retry. Temporal retries by default because most failures are
transient. Deciding which are not is your job.

## Without Temporal

The same two outages against a bare Agents SDK process:

```python
result = await Runner.run(agent, input=question)   # raises, and that is the end of it
```

```text
openai.APIConnectionError: Connection error.
Traceback (most recent call last):
  ...
```

The process exits. The conversation is gone. On the next run the model re-reads the question,
re-calls every tool, and you pay for all of it again. `try`/`except` around `Runner.run` retries the
whole loop from the top, which is not the same as resuming it.

The MCP server, meanwhile, kept working through all of this: it is a local child process. The
fragile edge is the network hop, and that is the edge Temporal makes survivable.

## Prerequisites

Same as module 1.

## Run it

```bash
cd exercise && uv sync
uv run python -m worker
uv run python -m start_workflow "Which AI track sessions are on Saturday, and what is the weather in Melbourne?"
```

Task queue: `failure-lab-tq`.
