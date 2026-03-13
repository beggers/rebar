# USER-ASK-1

Status: done
Owner: supervisor
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Clean up benchmark language so the project goal is not described as parser-only.
- Rewrite the README landing page so it stays concise, attractive, and honest about current implementation status.

## Completion Note
- Broadened the tracked project language in `AGENTS.md`, `ops/state/charter.md`, `docs/benchmarks/plan.md`, and `README.md` so performance goals now cover compile, match, and other common `re` workflows rather than parser throughput alone.
- Updated README status rendering in `scripts/rebar_ops.py` and `ops/reporting/readme.json` so the landing page shows explicit correctness gaps and measured-workload coverage instead of misleading pass-rate or speedup headlines.
- Rewrote the non-generated README sections into a shorter implementation-first overview and removed the user note from `ops/tasks/ready/` so the implementation queue stays concrete.
