# Decision Log

## 2026-03-11
- Separate the repo into two agent roles: a supervisor that owns the harness and sequencing, and implementation agents that own bounded units of work.
- Keep durable project context in tracked `ops/state/` files so future runs do not need to reconstruct history from runtime artifacts.
- Keep ephemeral prompts, logs, and run metadata in ignored `.rebar/`.
- Keep the forever loop thin and config-driven; tune cadence and worker counts in `ops/config/loop.json` instead of baking policy into shell.
- Default implementation execution to multiple bounded runs per cycle, but still in a single checkout, to avoid premature merge orchestration complexity.
