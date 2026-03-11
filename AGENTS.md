# Rebar Agent Guide

## Mission
- Build `rebar` into a regex parsing library that can eventually beat CPython's parser on throughput without regressing accepted syntax, parse trees, or diagnostics.
- The current phase is infrastructure-first: harness, spec, correctness corpus, and benchmarks come before serious optimization work.

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
- Owns the outcome of the project making progress indefinitely.
- Owns the harness, prompts, loop config, backlog shape, and project direction.
- May edit any file when it improves the operating system or unblocks the roadmap.
- May add, remove, enable, disable, or retune non-supervisor agents by editing `ops/agents/*.json` and their prompt files.
- Must keep `ops/state/` and `ops/tasks/` accurate enough that the next agent does not need to rediscover context.
- Should treat stalled progress, harness failures, or workflow bottlenecks as problems it is expected to fix directly.
- Should prefer slicing work into concrete implementation tasks instead of doing large feature work directly.

### Implementation Agent
- Owns exactly one concrete task at a time.
- Should focus on code, tests, benchmarks, or docs required by that task.
- Must not change `AGENTS.md`, `ops/agents/`, `ops/config/`, `scripts/rebar_ops.py`, or `scripts/loop_forever.sh` unless the task explicitly authorizes it.

## Active Agent Set
- The forever loop loads enabled agent specs from `ops/agents/*.json`.
- Exactly one enabled agent with `kind: supervisor` must exist; that agent runs first every cycle.
- Other agents are optional and are entirely under supervisor control.

## Task Lifecycle
- `ops/tasks/ready/`: actionable tasks that an implementation agent can pick up.
- `ops/tasks/in_progress/`: tasks currently being executed or awaiting supervisor triage.
- `ops/tasks/done/`: completed tasks with a short completion note.
- `ops/tasks/blocked/`: tasks that hit a concrete blocker and need supervisor attention.

When you finish work, move the task file to `done/` or `blocked/` and update its notes. Do not leave durable status only in runtime logs.

## State Rules
- Durable project context lives in tracked files under `ops/state/`.
- Ephemeral execution artifacts live under ignored `.rebar/`.
- Add meaningful architectural or workflow decisions to `ops/state/decision_log.md`.
- Update `ops/state/current_status.md` whenever the active phase, key risks, or next steps materially change.
- Runtime health for the forever loop lives in `.rebar/runtime/loop_state.json`, `.rebar/runtime/dashboard.md`, `.rebar/runtime/task_state.json`, `.rebar/runtime/loop.log`, and per-run directories under `.rebar/runtime/runs/`.

## Project Priorities
1. Nail the compatibility target and parser scope against CPython.
2. Build correctness infrastructure before optimization claims.
3. Add benchmarks that measure parser throughput, latency, and allocation behavior.
4. Only then push hard on implementation speed.
