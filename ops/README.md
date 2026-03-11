# Rebar Ops

This directory is the tracked operating system for the project.

## Layout
- `agents/`: prompt bodies plus JSON agent specs that define who runs.
- `config/`: loop policy and Codex runner settings.
- `state/`: durable project context that future runs should read first.
- `tasks/`: task queue and task template.

## Workflow
1. The loop loads enabled agent specs from `ops/agents/*.json`.
2. The enabled supervisor runs first every cycle and owns keeping the system making progress forever.
3. Other enabled agents run afterward according to their dispatch policy.
4. Task workers consume ready tasks one at a time and should move them to `done/` or `blocked`.
5. `scripts/loop_forever.sh` re-invokes one bounded `cycle` at a time, so repo changes take effect on the next pass.
6. The harness auto-recovers stale `in_progress` tasks, syncs the tracked README status block, auto-commits and auto-pushes repo changes, and writes a dashboard after each cycle.
7. Runtime prompts, logs, metadata, task state, and anomaly summaries are written to ignored `.rebar/runtime/`.

## Why It Exists
- Future agent runs should not need to infer project history from scratch.
- The supervisor needs a durable place to record decisions and retune the harness.
- Implementation agents need a narrow, concrete queue instead of a vague project brief.
