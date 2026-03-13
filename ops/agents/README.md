# Agent Registry

Each enabled `*.json` file in this directory defines one agent that the forever loop may run.

## Required Fields
- `name`: stable agent name
- `kind`: `supervisor`, `task_worker`, or another worker category you introduce
- `prompt_path`: prompt file to render for the agent
- `dispatch.mode`: how the loop schedules the agent

## Common Dispatch Modes
- `every_cycle`: run once every cycle
- `interval`: run when `interval_seconds` has elapsed
- `task_queue`: claim tasks from a queue and run once per claimed task

## Conventions
- Exactly one enabled agent with `kind: supervisor` must exist.
- The supervisor may add, remove, enable, disable, or retune non-supervisor agents by editing this directory.
- The supervisor is the only agent that may touch the harness or agent operating model.
- `USER-ASK` items that concern the harness should be treated as supervisor-owned work.
- `USER-ASK` notes belong in `ops/user_asks/inbox/`, not in `ops/tasks/ready/`.
- The current harness has one shared tracked task lane: `ready -> in_progress -> done|blocked`.
- Task workers may share `ready/` when they route claims by task `Owner:` instead of by separate directories.
- The current owner-routed task workers are `feature-implementation` for feature/parity work and `architecture-implementation` for refactor/architecture work.
- Specialist agents that plan, review, report, or repair outside the queue should usually use `every_cycle` or `interval`.
