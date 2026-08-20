# Durable AI Agents Workshop

A 2-hour path from a bare agent to one that survives an outage, built with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and [Temporal](https://temporal.io/)
for durable execution. Four modules, each adding one thing, so you can see before and after in the
Temporal Web UI.

## Author

## 🚀 Nikolay Advolodkin

🤖 **AI Agents & Distributed Systems** specializing in durable execution, Temporal workflows, and AI-powered applications

🎓 **Educator** | Trained **150,000+ engineers** across **190 countries**

🎤 **International Speaker** | Presented at Agentic AI Summit, SauceCon, Productivity Conf, DeveloperWeek, Selenium Conference & more.

📚 **Content Creator** | [LinkedIn](https://www.linkedin.com/in/nikolayadvolodkin/) | [YouTube](https://www.youtube.com/ultimateqa?sub_confirmation=1) | [Blog](https://ultimateqa.com/blog)

## Inspiration

This workshop was inspired by [Cornelia Davis'](https://www.linkedin.com/in/corneliadavis/) original
[AI Agents Workshop](https://github.com/temporal-community/ai-agents-workshop-python).

## Modules

| Module | What's new | Read this first |
|---|---|---|
| [`modules/01-durable-agent`](modules/01-durable-agent/) | An OpenAI Agents SDK agent inside a Temporal workflow. One LLM call, already durable, no tools yet. | [`modules/01-durable-agent/README.md`](modules/01-durable-agent/README.md) |
| [`modules/02-durable-tools`](modules/02-durable-tools/) | Tools become Temporal activities via `activity_as_tool`. Each tool call gets its own retry policy and history entry. | [`modules/02-durable-tools/README.md`](modules/02-durable-tools/README.md) |
| [`modules/03-mcp`](modules/03-mcp/) | A local MCP server (`modules/mcp-server`) joins the activity tools. Each `listTools`/`callTool` becomes a Temporal activity too. | [`modules/03-mcp/README.md`](modules/03-mcp/README.md) |
| [`modules/04-failure`](modules/04-failure/) | The module 3 agent, unchanged, put under three failures: a dead network, a killed worker, and a request that should never be retried. | [`modules/04-failure/README.md`](modules/04-failure/README.md) |

## How to work through the workshop

Each module's README is a self-contained walkthrough. The rough shape every time:

1. Start a Temporal dev server once (`temporal server start-dev`). All modules connect to `localhost:7233`.
2. Set `OPENAI_API_KEY` in your shell.
3. `cd modules/NN-.../exercise && uv sync` (or `solution/` to run the finished reference directly).
4. Fill in the `TODO`s in `exercise/` (see that module's README for what's missing).
5. Run the worker in one terminal: `uv run python -m worker`.
6. Run a workflow in another: `uv run python -m start_workflow "<your prompt>"`.

Every module uses a distinct Temporal task queue, so workers can run side by side without
interfering with each other. Modules 3 and 4 also need `modules/mcp-server`, located via
`MCP_SERVER_HOME`, which defaults to that path relative to each module.

## Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** - `brew install uv` on macOS.
- **[Temporal CLI](https://docs.temporal.io/cli)** - `brew install temporal` on macOS.
- **OpenAI API key** - set as `OPENAI_API_KEY`.

Nothing else. No Node, no JDK, no external MCP server to clone.

## Observing what Temporal gives you

All modules are Temporal workflows, so you can watch them in the Temporal Web UI at
http://localhost:8233. Module 2's tool calls appear as activities automatically. Module 3 adds MCP
`listTools`/`callTool` activities alongside them. Module 4 is where it pays off: kill the network or
the worker mid-run and watch the same workflow execution pick up where it stopped.

Every module also sends traces to OpenAI's trace dashboard at https://platform.openai.com/traces, so
you can see the agent's reasoning alongside the Temporal-side history.

## Project layout

```
.
├── README.md                                   # this file
├── justfile                                    # Instruqt CLI wrapper
├── instruqt/                                   # Instruqt track definition
│   ├── track.yml  config.yml
│   ├── track_scripts/                          # track-level setup/cleanup
│   ├── docker/                                 # sandbox Dockerfile + network control panel
│   └── 01-durable-agent/ ... 05-recap/         # one dir per challenge
└── modules/
    ├── mcp-server/                              # shared FastMCP stdio server (modules 3-4)
    ├── 01-durable-agent/
    │   ├── exercise/                            # TODOs for you to fill in
    │   └── solution/                            # finished reference
    ├── 02-durable-tools/
    │   ├── exercise/
    │   └── solution/
    ├── 03-mcp/
    │   ├── exercise/
    │   └── solution/
    └── 04-failure/
        ├── exercise/
        └── solution/
```

## Instruqt track

This repo is also the source for a hands-on Instruqt lab: five challenges (four modules plus a
closing quiz) in a browser-based sandbox, no local setup required.

### What the sandbox image bakes in

- Python 3.12 + `uv`, the Temporal CLI
- All four modules' `exercise/` and `solution/` dependencies, plus the MCP server's, pre-synced with `uv sync`
- `mitmproxy` with a trusted CA cert, used by the network control panel to fault-inject external calls
- Every module's `.venv/certifi` bundle patched with the proxy's CA, so proxied HTTPS calls succeed

### Tab inventory per challenge

Every coding challenge has a **Worker** terminal, a **Starter** terminal, a **Temporal UI** tab
(port 8233), a **Network Control Panel** tab (port 5000, a Flask app that toggles the mitmproxy
addon per external service), an **Editor** tab (native `type: code`), and a **Solution** tab.

### LLM access (per-attendee keys via the LiteLLM secret broker)

Attendees never supply an API key, and there is no shared key. Every attendee gets their own
short-lived, budget-capped key to a managed LiteLLM gateway, minted at lab start.

#### The one secret you need

The track declares exactly one secret in `config.yml`:

```yaml
secrets:
- name: TEMPORAL_LITELLM_BROKER_SECRET
```

`TEMPORAL_LITELLM_BROKER_SECRET` is **not an OpenAI key**. It's an HMAC signing secret the broker
uses to authenticate the sandbox's request. It is **team-scoped** in Instruqt (Team Settings >
Secrets), so it already exists and is shared across Temporal's tracks. There is no per-track value
to set and no OpenAI key to rotate. It must be present, or setup aborts immediately with
`TEMPORAL_LITELLM_BROKER_SECRET is not set`.

#### What happens at lab start

`track_scripts/setup-workshop` does this (see `mint_litellm_token`):

1. Downloads the `secret-broker` CLI installer from S3 (`SECRET_BROKER_BASE_URL`) and installs it. `curl` retries up to 10 times, so a transient network blip self-heals.
2. Runs `secret-broker litellm --duration=1d --budget=5`. The CLI signs a request with `TEMPORAL_LITELLM_BROKER_SECRET`, calls the broker, and the broker mints a **per-attendee LiteLLM virtual key** scoped to this track.
3. Writes OpenAI-compatible env vars (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`) to `/root/.litellm-env`, bridged into every attendee terminal's `.bashrc`.

The workshop code is unchanged: it uses the OpenAI SDK normally. `OPENAI_BASE_URL` points at the
LiteLLM gateway instead of `api.openai.com`. The gateway holds the real upstream OpenAI credentials
centrally; they never touch a sandbox. `setup-workshop` also patches the network control panel so
the "OpenAI" fault-injection toggle disrupts the gateway host.

#### Configuration knobs (all have defaults, override via track env vars)

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_BROKER_BASE_URL` | S3 bucket URL | Where the `secret-broker` installer is fetched from |
| `SECRET_BROKER_VERSION` | `main` | Installer version/channel |
| `LITELLM_KEY_DURATION` | `1d` | TTL of each minted key |
| `LITELLM_MAX_BUDGET` | `5` | Per-key spend cap in USD |
| `INSTRUQT_LITELLM_TRACK_ID` | the track slug | Track id sent to the broker |
| `OPENAI_MODEL` | `gpt-4o` | Model the modules request through the gateway |
| `LITELLM_PROXY_HOST` | `litellm-instruqt.tmprl-demo.cloud` | Gateway host the proxy panel toggles |

#### Why per-attendee keys, not one shared OpenAI key

For a small, trusted run a single shared `OPENAI_API_KEY` secret works. At conference scale it does
not: one shared key hits OpenAI's per-org rate limits under synchronized load, and it is readable in
every attendee's sandbox, so it is a leak and abuse liability. Per-attendee keys fix both: each key
has its own budget and rate scope, one attendee cannot starve or bill the others, and a leaked key is
capped and expires in a day.

#### Troubleshooting

- **"Failed to start track"** - the mint runs under `set -e`, so any failure in `setup-workshop`
  aborts the whole lab start. Run `instruqt track test` from `instruqt/` to see the real cause: on
  failure it prints the setup log, including the exact `curl`/broker error.
- **`instruqt track test` runs your LOCAL track files, not the deployed track.** You can validate a
  `setup-workshop` change before pushing, but a green local test does not prove the deployed track
  is fixed until you push.
- **The image is not involved.** The `secret-broker` installer is fetched from S3 at runtime, and
  `setup-workshop` is part of the track definition. Changing it needs only `instruqt track push`,
  never a sandbox image rebuild.
- **Do not silently fall back to a shared `OPENAI_API_KEY`** for anything beyond a small internal
  test. Fix the broker path instead.

### Network control panel

The control panel toggles external services on and off mid-module so attendees can watch Temporal
retry a failing activity and resume once the service comes back: OpenAI and Weather. It is driven by
`instruqt/docker/proxy/controlpanel.py` and `toggle_addon.py`, both started by
`track_scripts/setup-workshop`.

### Instruqt CLI workflow

```bash
just validate       # instruqt track validate
just push            # instruqt track push
just pull            # instruqt track pull (populates server-assigned ids)
just test            # instruqt track test (runs check/solve scripts end to end)
```

First-time track creation:

```bash
just create                      # registers the slug server-side, once
just init                        # instruqt track push --force
just pull
git add instruqt/ && git commit -m "Pin Instruqt track and tab ids"
```

### Publishing (manual, no CI)

There is no GitHub Actions pipeline; publishing is manual, and what you run depends on what changed:

- **Changed an `assignment.md`, lifecycle script, `track.yml`, or `config.yml`** (anything under
  `instruqt/`): run `instruqt track push`. No image rebuild.
- **Changed exercise/solution code or the `Dockerfile`** (`modules/*`, `instruqt/docker/`): rebuild
  and push the image, then launch a fresh sandbox to pick it up:
  ```bash
  docker buildx build --platform linux/amd64 \
    -f instruqt/docker/Dockerfile \
    -t trainwithshubham/durable-ai-agents-workshop-sandbox:latest --push .
  ```

`instruqt track test` runs the track's local files against the deployed image, so it's the way to
verify a change before pushing.

**A push that fails the delta check applies nothing.** When the deployed track's checksum has
drifted from `checksum:` in the local `track.yml`, push stops at `==> Checking deltas` with
`There are remote changes for this track` and the remote is left untouched. Do not read that
`[ERROR]` as "pushed anyway".

> [!WARNING]
> **`checksum:` is self-poisoning; commit it after every publish.** That field is an
> optimistic-concurrency token recording the last known deployed state. A successful publish changes
> the deployed checksum and writes the new value into your local `track.yml`. If you don't commit
> it, the next person's push fails the delta check until they resync by hand.

**Tab ids drift.** Pinned `id:` values for service tabs can go stale. After any push, run
`instruqt track pull`, re-pin the ids from the `*.remote` files, and delete the leftovers
(`just clean-remote`).

**Number challenge directories from `01`, never `00`.** A challenge in a `00-` directory is silently
dropped on publish: `instruqt track validate` passes, `instruqt track push` reports success, and the
challenge simply does not exist on the platform. `validate` accepts a sequence starting at either
`00` or `01`, so nothing warns you.
