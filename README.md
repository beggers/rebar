# rebar

`rebar` is an agent-operated regex parser R&D repo. The target is a parser that is eventually faster than the one CPython uses, without giving up syntax compatibility or correctness.

This repo is currently bootstrapped as a control plane:
- `ops/` contains role prompts, durable project state, loop policy, and the task queue.
- `ops/agents/*.json` defines the active agent set that the supervisor may change over time.
- `scripts/rebar_ops.py` runs supervisor-first cycles and dispatches the enabled agents.
- `.rebar/` is the ignored runtime area for prompts, logs, and run metadata.

## Current Development Order
1. Define the compatibility target and parser scope.
2. Build correctness and benchmark harnesses.
3. Implement the parser.
4. Optimize based on measured bottlenecks.

## Useful Commands

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py render supervisor
python3 scripts/rebar_ops.py cycle --force-supervisor
bash scripts/loop_forever.sh
```

The normal place to tune cadence and worker counts is `ops/config/loop.json`. The shell wrapper is intentionally thin.
