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
- Task workers should usually use `dispatch.mode = "task_queue"` and claim from `ready` into `in_progress`.
