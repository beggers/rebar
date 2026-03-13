# USER-ASK-4

Status: done
Owner: supervisor
Created: 2026-03-13
Completed: 2026-03-13

## Goal
- Stop the generated README reporting from growing into a feature inventory, and fix the harness/prompt path so future supervisor passes keep the landing page concise by default.

## Completion Note
- Updated `scripts/rebar_ops.py` and `ops/reporting/readme.json` so the README status block now reads dedicated short `README ...` summary sections from `ops/state/current_status.md` instead of streaming the full detailed compatibility and risk sections straight into the landing page.
- Added explicit renderer caps for README next-step and risk bullets, so richer internal state no longer expands the landing page automatically.
- Updated `ops/agents/supervisor.md`, `ops/README.md`, `ops/state/backlog.md`, and `ops/state/decision_log.md` so the operating model now requires those README summary sections to stay short and high-level.
- Shortened the hand-written README overview sections so the landing page gives a rough delivery estimate and near-term direction instead of another growing feature list.
