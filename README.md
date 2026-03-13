# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is widening a real Rust-backed subset, but the project is still early relative to the drop-in `re` target. |
| Delivery estimate | Foundation work is complete, the published slice is expanding through benchmark catch-up and exact follow-on tasks, and overall stdlib-parity progress is still in the early implementation stage. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `8` ready, `0` in progress, `236` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `548` |
| Passing in published slice | `532` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `16` |
| Covered manifests | `69` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, the published slice is expanding through benchmark catch-up and exact follow-on tasks, and overall stdlib-parity progress is still in the early implementation stage._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `396` |
| Workloads with real `rebar` timings | `359` |
| Known-gap workloads | `37` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `359` of `396` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0228` through `RBR-0230` so the first exact open-ended `{1,}` quantified-alternation follow-on reaches the published benchmark surface.
- Then land `RBR-0231` through `RBR-0233`, with `RBR-0234` through `RBR-0236` already seeded behind them for the wider ranged-repeat quantified-group alternation follow-on.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Local git history is diverged from `origin/main`, so the loop cannot auto-push until the remote-only `USER-ASK-4` and `USER-ASK-5` commits are reconciled.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` now has the hard part of the operating system in place: a supervisor/worker loop, durable state, honest correctness and benchmark publication, a Rust core crate, and a CPython-facing extension boundary. The implementation itself is real but still narrow. The exact published counts live in the generated status block above; the short version is that the first bounded two-arm, alternation-heavy two-arm, nested two-arm, and quantified two-arm conditional replacement slices reach the Rust-backed correctness baseline, the repo carries a strict built-native full-suite benchmark sidecar, the conditional-plus-branch-local-backreference and quantified-alternation-plus-conditional slices already reach both Rust-backed correctness and published benchmark coverage, the quantified-alternation nested-branch, backtracking-heavy, and broader-range `{1,3}` slice now also reaches published benchmark coverage, and the active queue now leads with `RBR-0228` through `RBR-0230` for the open-ended `{1,}` follow-on, then `RBR-0231` through `RBR-0233` for one exact-repeat quantified-group alternation follow-on, with `RBR-0234` through `RBR-0236` already seeded behind them for the wider ranged-repeat quantified-group alternation follow-on.

The practical read is simple: infrastructure is no longer the blocker, and compatibility work is progressing in small Rust-backed slices. The tracked frontier already includes deterministic corpus coverage, multiple bounded conditional execution and replacement slices, quantified branch-local-backreference work, and quantified-alternation combinations through the broader-range `{1,3}` frontier, while the next exact follow-ons remain explicit. The immediate follow-ons are `RBR-0228` through `RBR-0230` for the open-ended quantified-alternation trio, then `RBR-0231` through `RBR-0233` for exact-repeat quantified-group alternation, with `RBR-0234` through `RBR-0236` already seeded behind them for wider ranged-repeat quantified-group alternation.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the primary full-suite report still times the source-tree shim, `reports/benchmarks/native_full.json` records the latest checked-in strict built-native full-suite sidecar, and `reports/benchmarks/native_smoke.json` remains the quick six-workload native check.

## What The Numbers Mean

The correctness report is a slice-health signal, not an end-state signal. The current publication covers 532 cases across 68 manifests, with all 532 passing and no honest `unimplemented` gaps in the published slice, and that still does not mean the project is close to replacing stdlib `re` across the board. The immediate queue is `RBR-0228` through `RBR-0236` to take one exact open-ended quantified-alternation follow-on, then one exact-repeat quantified-group alternation follow-on, then one wider ranged-repeat quantified-group alternation follow-on through the same publish/parity/benchmark sequence.

The benchmark report is still a coverage-first artifact too. It already exercises a wide workload set, but dozens of workloads are still explicit gaps and the main published run still measures the source-tree shim rather than the fully built-native path. That is enough to guide the queue, but not enough to make broad speed claims yet.

## Operating Model

The repo runs with a supervisor/implementation split. The supervisor maintains the harness, queue, state files, and README/reporting surfaces. The implementation worker takes one bounded task at a time and moves it to `done/` or `blocked/`. Durable context lives under `ops/state/`; ephemeral execution traces live under `.rebar/runtime/`.

## Important Paths

| Path | Purpose |
| --- | --- |
| `ops/state/current_status.md` | Durable project status, risks, and near-term next steps. |
| `ops/state/backlog.md` | Ordered milestone queue plus supervisor notes about sequencing. |
| `ops/tasks/` | Ready, in-progress, done, and blocked task queues. |
| `.rebar/runtime/dashboard.md` | Latest cycle health, git state, and queue counts. |
| `reports/correctness/latest.json` | Latest published correctness scorecard. |
| `reports/benchmarks/latest.json` | Latest published full benchmark scorecard, currently through the source-tree shim. |
| `reports/benchmarks/native_full.json` | Strict built-native sidecar for the full published benchmark suite. |
| `reports/benchmarks/native_smoke.json` | Dedicated built-native smoke benchmark artifact for the verified `rebar._rebar` path. |
| `python/rebar/__init__.py` | Current Python-facing shim and scaffold behavior. |
| `python/rebar_harness/` | Correctness and benchmark runners. |

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
- Do not start a second `python3 scripts/rebar_ops.py cycle ...` run against the same checkout while `scripts/loop_forever.sh` is active.
- Avoid launching the loop from inside another sandboxed Codex session; nested sandboxes can distort child-agent behavior and cache writes.
- The supervisor is expected to change the harness, reporting, and queue when that is the pragmatic way to keep the project moving.
