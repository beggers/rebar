# Task Queue

Task files move through these directories:
- `ready/`
- `in_progress/`
- `done/`
- `blocked/`

Use `templates/task-template.md` for new tasks. Keep tasks concrete:
- name the target files when possible
- include acceptance criteria
- state any files that are out of scope

`ops/tasks/ready/` is a single shared lane consumed by the Feature Implementation Agent.
Architecture and Feature Planning agents may add ready tasks, but queued tasks should normally set `Owner: feature-implementation`.
The Feature Implementation Agent owns moving its assigned task to a terminal queue.
`USER-ASK` notes should not be placed in `ops/tasks/`; put them in `ops/user_asks/inbox/` for the supervisor instead.
