# Rebar Ops

This directory is the tracked operating system for the project.

## Layout
- `agents/`: prompt bodies for the supervisor and implementation roles.
- `config/`: loop policy and Codex runner settings.
- `state/`: durable project context that future runs should read first.
- `tasks/`: task queue and task template.

## Workflow
1. The supervisor reads the state files, updates project direction, and makes sure `tasks/ready/` contains concrete work.
2. Implementation agents consume ready tasks one at a time.
3. Each implementation run should either move its task to `done/` or `blocked/`.
4. Runtime prompts, logs, and metadata are written to ignored `.rebar/runtime/`.

## Why It Exists
- Future agent runs should not need to infer project history from scratch.
- The supervisor needs a durable place to record decisions and retune the harness.
- Implementation agents need a narrow, concrete queue instead of a vague project brief.
