# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython on parser throughput without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

Capability-track coverage: `[##################] 100%`

_This measures whether the planned scaffolds, plans, and scorecard artifacts exist. It does not mean `rebar` already matches CPython's `re` feature-for-feature._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance pack published, and the remaining benchmark/module-surface gaps queued. |
| Current milestone | Milestone 2: finish the remaining Phase 1 benchmark expansion and Phase 2 module-surface harness work on top of the landed parser conformance pack, verified native-extension smoke path, and exact CPython baseline metadata. |
| Work queue | `5` ready, `0` in progress, `13` done, `0` blocked |
| Capability tracks | `10/10` complete |

### Capability Matrix

| Capability | Status | Evidence |
| --- | --- | --- |
| Drop-in `re` compatibility contract | complete | [`docs/spec/drop-in-re-compatibility.md`](docs/spec/drop-in-re-compatibility.md) |
| Syntax compatibility scope | complete | [`docs/spec/syntax-scope.md`](docs/spec/syntax-scope.md) |
| Correctness plan | complete | [`docs/testing/correctness-plan.md`](docs/testing/correctness-plan.md) |
| Benchmark methodology | complete | [`docs/benchmarks/plan.md`](docs/benchmarks/plan.md) |
| Rust parser crate scaffold | complete | [`crates/rebar-core/src/lib.rs`](crates/rebar-core/src/lib.rs) |
| CPython extension scaffold | complete | [`crates/rebar-cpython/src/lib.rs`](crates/rebar-cpython/src/lib.rs) |
| Automated conformance harness | complete | [`python/rebar_harness/correctness.py`](python/rebar_harness/correctness.py) |
| Automated benchmark harness | complete | [`python/rebar_harness/benchmarks.py`](python/rebar_harness/benchmarks.py) |
| Published correctness scorecard | complete | [`reports/correctness/latest.json`](reports/correctness/latest.json) |
| Published benchmark scorecard | complete | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

### Correctness Scorecard

| Metric | Value |
| --- | --- |
| Candidate | rebar |
| Cases | `0` / `15` |
| Pass rate | `0.0` |
| Parity rate | `0.0` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Parser Benchmark Scorecard

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Candidate | rebar |
| Workloads | `6` |
| Geomean speedup vs baseline | `None` |
| Median speedup vs baseline | `None` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

### Immediate Next Steps

- Land `RBR-0012` to bring the benchmark harness up to the same Phase 1 compile-matrix depth that correctness now has.
- Land `RBR-0013`, `RBR-0014`, and `RBR-0015` so the repo exposes a broader scaffolded `re` helper surface and the scorecards can separate parser progress from public-API and module-boundary progress.
- Keep `RBR-0016` and `RBR-0017` queued behind Milestone 2 so the worker can continue directly into match-behavior correctness and regression/stability benchmark infrastructure without another supervisor-only queue rewrite.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path, but the published benchmark report still reflects the source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface is still minimal, so public-API correctness and module-boundary benchmarking remain blocked on additional placeholder exports even though the native extension now imports successfully.
- The correctness harness now covers 15 parser compile cases, but it still reports `unimplemented` for every `rebar` comparison and does not yet measure helper presence, pattern objects, or match-result behavior.
- The benchmark harness currently measures only two parser-family compile smoke workloads and records no `rebar` timings yet, so timing provenance is still only baseline-side scaffolding.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has only eleven completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
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
- `reports/correctness/latest.json` is the source of truth for the latest committed correctness scorecard.
- `reports/benchmarks/latest.json` is the source of truth for the latest committed benchmark scorecard.

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
- Do not start a second `python3 scripts/rebar_ops.py cycle ...` run against the same checkout while `scripts/loop_forever.sh` is active. The harness now serializes cycle runs with a runtime lock and rejects overlapping manual cycles instead of racing the live loop.
- Avoid launching the loop from inside another sandboxed Codex session; nested sandboxes can clamp child agents or their cache writes.
- The supervisor is allowed to change the harness, prompts, repo structure, reporting config, and active agent set when that is the pragmatic way to keep the project moving.
