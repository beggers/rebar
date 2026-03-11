# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython on parser throughput without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

Feature completeness: `[##................] 11%`

| Signal | Value |
| --- | --- |
| Phase | Phase 1: harness bootstrap and project-definition work for a Rust drop-in `re` replacement. |
| Current milestone | Milestone 1: define the Rust implementation target and drop-in `re` compatibility contract well enough that implementation work can start without re-litigating scope each run. |
| Work queue | `4` ready, `0` in progress, `0` done, `0` blocked |
| Capability tracks | `0/9` complete |

### Capability Matrix

| Capability | Status | Evidence |
| --- | --- | --- |
| Drop-in `re` compatibility contract | planned | [`ops/tasks/ready/RBR-0000-rust-drop-in-target.md`](ops/tasks/ready/RBR-0000-rust-drop-in-target.md) |
| Syntax compatibility scope | planned | [`ops/tasks/ready/RBR-0001-initial-syntax-scope.md`](ops/tasks/ready/RBR-0001-initial-syntax-scope.md) |
| Correctness plan | planned | [`ops/tasks/ready/RBR-0002-correctness-harness-plan.md`](ops/tasks/ready/RBR-0002-correctness-harness-plan.md) |
| Benchmark methodology | planned | [`ops/tasks/ready/RBR-0003-benchmark-plan.md`](ops/tasks/ready/RBR-0003-benchmark-plan.md) |
| Rust parser crate scaffold | not started | `not yet queued` |
| CPython extension scaffold | not started | `not yet queued` |
| Automated conformance harness | not started | `not yet queued` |
| Published correctness scorecard | not started | `not yet queued` |
| Published benchmark scorecard | not started | `not yet queued` |

### Correctness Scorecard

No published correctness scorecard yet. Expected tracked source: [`reports/correctness/latest.json`](reports/correctness/latest.json).

### Parser Benchmark Scorecard

No published benchmark scorecard yet. Expected tracked source: [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json).

### Immediate Next Steps

- Let the next bypass-configured implementation retry consume one of the seeded spec tasks; if it still does not move, treat that as a worker or harness regression rather than a sandbox mystery.
- Use the implementation agent to write the Rust drop-in target, syntax spec, correctness plan, and benchmark plan documents now that bypass-mode child writes and probe validation are both in place.
- After those land, start Rust crate scaffolding, CPython-extension scaffolding, and the first parser tests.

### Current Risks

- The project can drift into premature implementation without a clear compatibility target.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Nested supervisor runs inside a live forever loop can still create misleading runtime anomalies even when the underlying worker write path is healthy.
<!-- REBAR:STATUS_END -->

## What `rebar` Is Trying To Do

- Match the parser-facing and user-facing behavior that matters from CPython's `re` stack.
- Expose the implementation through a CPython-facing module so users can import it as a drop-in replacement for `re`.
- Prove correctness before making speed claims.
- Publish benchmark results against a concrete baseline instead of hand-waving about performance.
- Keep project state durable in tracked files so autonomous runs can pick up where the last one left off.

## How The Project Works

`rebar` is organized around a supervisor/worker split:

- The supervisor owns direction, backlog quality, harness health, reporting, and the long-term outcome of the loop making progress forever.
- Implementation agents own bounded tasks such as spec docs, test harnesses, benchmark harnesses, Rust crates, CPython-extension glue, parser code, and performance work.
- The outer loop is intentionally tiny. It re-runs one bounded cycle at a time so changes to prompts, config, code, and active agents apply on the next iteration.

## Development Priorities

1. Define the exact syntax and compatibility target.
2. Build correctness infrastructure.
3. Build benchmark infrastructure.
4. Implement the Rust parser and CPython-facing module surface.
5. Optimize only after measurement makes the bottlenecks obvious.

## Repository Map

| Path | Purpose |
| --- | --- |
| `ops/` | Durable project operating system: prompts, state, reporting config, backlog, and task queue. |
| `ops/state/` | Human-readable project status, backlog, charter, and decision log. |
| `ops/tasks/` | Ready, in-progress, done, and blocked task queues for implementation work. |
| `ops/reporting/` | Tracked config that defines README-facing capability and benchmark reporting. |
| `scripts/rebar_ops.py` | Main harness entrypoint for bounded cycles, reporting, task recovery, and git sync. |
| `scripts/loop_forever.sh` | Thin forever-loop wrapper around repeated bounded cycles. |
| `.rebar/runtime/` | Ignored runtime artifacts such as logs, prompts, dashboard output, and loop state. |
| `docs/` | Specs, plans, and eventually parser-related design and testing docs. |
| `reports/` | Tracked published outputs such as correctness and benchmark scorecards. |

## Human Check-In Surfaces

- `README.md` is the tracked landing page for high-level current state and project capabilities.
- `.rebar/runtime/dashboard.md` is the runtime dashboard for operational details from the latest completed cycle.
- `ops/state/current_status.md` is the durable project-state document the supervisor is expected to keep accurate.
- `reports/correctness/latest.json` is the planned source of truth for the latest committed correctness scorecard.
- `reports/benchmarks/latest.json` is the planned source of truth for the latest committed parser benchmark scorecard once benchmarking exists.

## Useful Commands

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
python3 scripts/rebar_ops.py render supervisor
python3 scripts/rebar_ops.py cycle --force-agent implementation
python3 scripts/rebar_ops.py cycle --force-supervisor
bash scripts/loop_forever.sh
```

## Operating Notes

- Run the forever loop from a normal shell on a writable checkout.
- Avoid launching the loop from inside another sandboxed Codex session; nested sandboxes can clamp child agents or their cache writes.
- The supervisor is allowed to change the harness, prompts, repo structure, reporting config, and active agent set when that is the pragmatic way to keep the project moving.
