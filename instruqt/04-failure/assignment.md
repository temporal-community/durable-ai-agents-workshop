---
slug: failure
id: 2vhgrncqaukq
type: challenge
title: 'Module 4: Break It'
teaser: Kill the network, kill the worker, then decide which failures deserve a retry
  at all.
notes:
- type: text
  contents: |-
    # Kill the worker mid-thought

    The agent is four tool calls into a nine-step answer. You send SIGKILL to
    the process running it.

    Where does the loop go?
- type: text
  contents: |-
    # Retrying is not always right

    A 503 passes on the next attempt. A 400 will fail identically forever, and
    Temporal will keep paying for attempts until a timeout.

    Temporal retries by default. Deciding what not to retry is your job.
tabs:
- id: akoaefbbf1sb
  title: Worker
  type: terminal
  hostname: workshop
  workdir: /root/workshop/modules/04-failure/exercise
- id: 59gibrpiqw8w
  title: Starter
  type: terminal
  hostname: workshop
  workdir: /root/workshop/modules/04-failure/exercise
- id: ikdgiol1bimg
  title: Temporal UI
  type: service
  hostname: workshop
  path: /
  port: 8233
- id: 0wfp19d7ma5g
  title: Network Control Panel
  type: service
  hostname: workshop
  path: /
  port: 5000
- id: yfuljjpg5wd2
  title: Editor
  type: code
  hostname: workshop
  path: /root/workshop/modules/04-failure/exercise
- id: ltmtlm6ykyyb
  title: Solution
  type: code
  hostname: workshop
  path: /root/workshop/modules/04-failure/solution
difficulty: basic
timelimit: 1800
enhanced_loading: null
---

# Break It

Same agent as module 3. Three failures, one code change.

> [!NOTE]
> **Your tabs.**
> - [button label="Worker" background="#444CE7"](tab-0) runs the worker.
> - [button label="Starter" background="#444CE7"](tab-1) launches workflows.
> - [button label="Temporal UI" background="#444CE7"](tab-2) is the event history.
> - [button label="Network Control Panel" background="#444CE7"](tab-3) turns external services off.
> - [button label="Editor" background="#444CE7"](tab-4) is your working copy.
> - [button label="Solution" background="#444CE7"](tab-5) is the finished code.

## Start the Worker

Click the [button label="Worker" background="#444CE7"](tab-0) terminal.

```bash,run
uv run python -m worker
```

## 1. Take the Network Away

Click the [button label="Starter" background="#444CE7"](tab-1) terminal and start a long one.

```bash,run
uv run python -m start_workflow "List the Saturday sessions, then tell me the weather in Melbourne and in Sydney."
```

While it is running, click the [button label="Network Control Panel" background="#444CE7"](tab-3)
tab and toggle **OpenAI** off.

Now watch the [button label="Temporal UI" background="#444CE7"](tab-2) tab:

- Status stays **Running**.
- `invoke_model_activity` is **Retrying**, attempts climbing, backoff growing.
- Everything it already did is still **Completed** above it.

Toggle **OpenAI** back on. The next attempt succeeds and the same execution finishes.

Nothing restarted. The starter never knew. You wrote no retry code.

## 2. Kill the Worker

Start a workflow from the [button label="Starter" background="#444CE7"](tab-1) terminal, then kill
the worker within the next 10 seconds:

```bash,run
pkill -9 -f "modules/04-failure"
```

Those 10 seconds are not a race against the model. The workflow pauses on a
`workflow.sleep(...)` before it calls anything, so you have a fixed, reliable window every time.

The `-9` matters. A polite `SIGTERM` lets the SDK drain whatever it is holding, which is not the
failure worth demonstrating.

The [button label="Temporal UI" background="#444CE7"](tab-2) tab shows the workflow still
**Running**, parked on a `TimerStarted` event with no pending activity. Bring the worker back in the
[button label="Worker" background="#444CE7"](tab-0) terminal:

```bash,run
uv run python -m worker
```

> Same workflow id, same run, and it continues. Where was the conversation while the process was
> dead?

<details>
<summary>Answer</summary>

In event history, on the Temporal server. The loop's state was never in that process. The worker is
just something that executes steps, so a new one picks up from the last recorded step.

This is the difference between a retry and a resume. A retry starts the loop again. A resume
continues it.
</details>

## 3. Decide What Not To Retry

The control panel returns `503` when a service is off, which is exactly the kind of failure a retry
fixes. A `400` is not.

Do the `TODO` in `tool_activities.py` in the [button label="Editor" background="#444CE7"](tab-4)
tab, restart the worker, and force a bad request:

```bash,run
uv run python -m start_workflow "What is the weather at latitude 999 and longitude 999?"
```

The activity fails once and stops. `non_retryable=True` is how you tell Temporal that trying again
is pointless.

## Without Temporal

The same two outages against a plain Agents SDK script:

```python,nocopy
result = await Runner.run(agent, input=question)
```

```text,nocopy
openai.APIConnectionError: Connection error.
Traceback (most recent call last):
  ...
```

The process exits. The conversation is gone. The next run re-reads the question, re-calls every
tool, and you pay for all of it again. Wrapping that line in `try`/`except` retries the whole loop
from the top, which is not the same thing as continuing it.

## Summary

| Failure | Plain script | Under Temporal |
|---|---|---|
| API returns 503 | Raises, loop over | Activity retries, loop continues |
| Process is killed | Everything lost | New worker resumes the same run |
| API returns 400 | Raises, loop over | Retries until you mark it non-retryable |
| Work already done | Re-done and re-paid for | Still in history |
