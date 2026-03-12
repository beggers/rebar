# USER-ASK-2

Status: done
Owner: supervisor
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Keep real `rebar` behavior out of `python/rebar/__init__.py` and steer the project back toward a Rust-owned implementation boundary.

## Completion Note
- Merged the remote queue note into the local branch so the supervisor loop stopped reporting a fetched-but-diverged git anomaly.
- Recorded the directive in `ops/state/backlog.md` and `ops/state/decision_log.md` as durable project policy: new compatibility behavior belongs in `rebar-core` and `rebar._rebar`, while Python stays limited to exports, wrappers, cache/object plumbing, and FFI calls.
- Inserted `RBR-0037A` and `RBR-0042A` ahead of the remaining parser and workflow follow-ons, and retuned `RBR-0038` through `RBR-0049` so future queue items keep new behavior work on the Rust side of the boundary.
