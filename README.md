# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython on parser throughput without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

Capability-track coverage: `[##################] 100%`

_This measures whether the planned scaffolds, plans, and scorecard artifacts exist. It does not mean `rebar` already matches CPython's `re` feature-for-feature._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary benchmark pack and public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, benchmark adapter/provenance hardening in place, and the remaining correctness and honest-behavior gaps queued. |
| Current milestone | Milestone 2: finish the exported-symbol/pattern correctness wave on top of the landed benchmark-provenance hardening, then roll directly into the first honest-behavior slice for literal-only matching, compile-cache/purge observability, `escape()` parity, the first literal-only collection/replacement helpers, and their scorecard follow-ons on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exported-symbol scaffold, compiled-pattern scaffold, exact CPython baseline metadata, the Phase 2 public-API correctness scorecard, the first Phase 3 match-behavior smoke pack, the new regression/stability benchmark pack, and benchmark adapter/provenance reporting. |
| Work queue | `10` ready, `0` in progress, `22` done, `0` blocked |
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
| Cases | `12` / `38` |
| Pass rate | `0.3158` |
| Parity rate | `0.7059` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Parser Benchmark Scorecard

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Candidate | rebar |
| Workloads | `19` |
| Geomean speedup vs baseline | `2.8598` |
| Median speedup vs baseline | `2.8611` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

### Immediate Next Steps

- Land `RBR-0021` and `RBR-0022` so the newly landed exported-symbol and compiled-pattern scaffolds reach the published correctness scorecard immediately after the benchmark-provenance hardening from `RBR-0020`.
- Use `RBR-0023` through `RBR-0027` as the next slice after that scorecard/provenance wave so the queue turns the landed `Pattern` surface into narrow honest behavior, cache/purge observability, `escape()` parity, pattern-boundary benchmark coverage, and module-workflow correctness.
- Keep `RBR-0028` through `RBR-0031` directly behind the current literal/cache/escape slice so the queue extends from literal-only collection and replacement helpers straight into their correctness and benchmark scorecards instead of stalling after `RBR-0029`.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer, published match-behavior smoke coverage, CPython-shaped exported flags/constants, and a concrete `Pattern` scaffold, but compiled-pattern correctness coverage and concrete `Match` behavior are still outside the measured compatibility surface.
- The correctness harness still covers 28 published cases across parser, module-API, and match-behavior layers, but 21 `rebar` comparisons still end in honest `unimplemented` outcomes and there is no exported-symbol, compiled-pattern, or module-workflow layer yet.
- The benchmark harness now measures the six parser-family compile-path workloads, the eight-workload module-boundary pack, and the five-workload regression/stability pack with explicit adapter-mode provenance, but only import rows produce real `rebar` timings so helper-call comparisons are still mostly placeholder gaps and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has twenty completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
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
