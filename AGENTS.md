# Rebar Agent Guide

## Mission
- Build `rebar` into a Rust-backed, CPython-facing, bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without regressing accepted syntax, public API behavior, parse trees, or diagnostics.
- The current phase is infrastructure-first: harness, spec, correctness corpus, and benchmarks come before serious optimization work.
- The target repository shape is a standard-looking Python library codebase with Rust implementation underneath, a huge differential pytest suite that runs the same assertions against `re` and `rebar`, and a huge Python-based benchmark suite that runs the same workloads against both.
- Prefer plain Python and Rust source files over JSON blobs, bespoke intermediate data layers, or Rust-only test scaffolding. We do not need Rust tests in this repo.

## Mandatory Read Order
1. `README.md`
2. `ops/README.md`
3. `ops/state/charter.md`
4. `ops/state/current_status.md`
5. `ops/state/backlog.md`
6. `ops/state/decision_log.md`
7. Your assigned task file under `ops/tasks/`

## Roles

### Supervisor
- Owns the outcome of the project making progress indefinitely through the harness.
- Owns the harness, prompts, loop config, active agent set, and `USER-ASK` intake.
- May edit any file when it improves the operating system or unblocks the roadmap.
- May add, remove, enable, disable, or retune non-supervisor agents by editing `ops/agents/*.json` and their prompt files.
- Must keep the harness and `ops/user_asks/` flow accurate enough that the next agent does not need to rediscover context.
- Should treat stalled progress, harness failures, or workflow bottlenecks as problems it is expected to fix directly.
- Should route harness-oriented `USER-ASK`s itself instead of pushing them into the implementation task queue.
- Should inspect the quality of recent sub-agent work every cycle and retune weak prompts or dispatch policy immediately, preferably by deleting confusing prompt text before adding more.

### Implementation Agent
- Owns exactly one concrete task at a time.
- Should focus on code, tests, benchmarks, or docs required by that task.
- Must not infer a read-only environment from prior logs alone; if it claims an environment blocker, that claim must come from a direct write attempt in the current run.
- Must not change `AGENTS.md`, `ops/agents/`, `ops/config/`, `scripts/rebar_ops.py`, or `scripts/loop_forever.sh` unless the task explicitly authorizes it.

## Active Agent Set
- The forever loop loads enabled agent specs from `ops/agents/*.json`.
- Exactly one enabled agent with `kind: supervisor` must exist; that agent runs first every cycle.
- Other agents are optional and are entirely under supervisor control.
- The current intended order is: supervisor, architecture, architecture implementation, feature planning, feature implementation, QA/testing, implementation faithfulness, cleanup, then reporting.

## Task Lifecycle
- `ops/tasks/ready/`: actionable tasks that an implementation agent can pick up, routed by the task `Owner:` field when multiple implementation agents share the queue.
- `ops/tasks/in_progress/`: tasks currently being executed or awaiting supervisor triage.
- `ops/tasks/done/`: completed tasks with a short completion note.
- `ops/tasks/blocked/`: tasks that hit a concrete blocker and need supervisor attention.
- `ops/user_asks/inbox/`: supervisor-owned user notes and harness asks that must not enter `ops/tasks/ready/`.
- `ops/user_asks/done/`: archived `USER-ASK` notes after the supervisor has handled them.

When you finish work, move the task file to `done/` or `blocked/` and update its notes. Do not leave durable status only in runtime logs.

## Commit Policy
- The harness commits tracked changes immediately after each agent run.
- Commit subjects should read as `<agent-name>: <brief description>`.
- Commit bodies should capture more detail about what changed and what was verified.
- End every run with a concise final summary that makes those generated commits accurate and readable.

## State Rules
- Durable project context lives in tracked files under `ops/state/`.
- Ephemeral execution artifacts live under ignored `.rebar/`.
- Add meaningful architectural or workflow decisions to `ops/state/decision_log.md`.
- Update `ops/state/current_status.md` whenever the active phase, key risks, or next steps materially change.
- Feature Planning owns keeping `ops/state/backlog.md` and the queue/frontier portions of `ops/state/current_status.md` aligned with the actual ready queue.
- Runtime health for the forever loop lives in `.rebar/runtime/loop_state.json`, `.rebar/runtime/dashboard.md`, `.rebar/runtime/task_state.json`, `.rebar/runtime/loop.log`, and per-run directories under `.rebar/runtime/runs/`.
- The supervisor should watch the tracked JSON-blob count in runtime reporting and retune the harness if architecture-oriented agents are not burning it down.

## Project Priorities
1. Nail the drop-in `re` compatibility target and parser scope against CPython.
2. Build a huge backend-parameterized differential pytest suite that runs against both `re` and `rebar` and confirms they behave the same through the public Python surface.
3. Build a huge Python-based benchmark suite that runs equivalent workloads against both `re` and `rebar`.
4. Remove JSON blobs and other non-standard data-storage intermediaries so the repo looks as close as possible to a standard Python library codebase.
5. Only then push hard on Rust implementation speed.
