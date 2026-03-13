# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is widening a real Rust-backed subset, but the project is still early relative to the drop-in `re` target. |
| Delivery estimate | Foundation work is complete, the published slice is expanding with explicit honest gaps and catch-up tasks, and overall stdlib-parity progress is still in the early implementation stage. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `9` ready, `0` in progress, `179` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `364` |
| Passing in published slice | `364` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `50` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, the published slice is expanding with explicit honest gaps and catch-up tasks, and overall stdlib-parity progress is still in the early implementation stage._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `306` |
| Workloads with real `rebar` timings | `257` |
| Known-gap workloads | `49` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `257` of `306` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0171` to catch the bounded alternation-heavy empty-yes-arm slice up in benchmarks, then land `RBR-0172` through `RBR-0174` for the alternation-bearing fully-empty publication/parity/benchmark follow-on.
- Then land `RBR-0175` through `RBR-0180` for the bounded quantified omitted-no-arm and explicit-empty-else conditional follow-ons already anchored in the benchmark manifests.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Local git history is diverged from `origin/main`, so the loop cannot auto-push until the remote-only `USER-ASK-4` and `USER-ASK-5` commits are reconciled.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` now has the hard part of the operating system in place: a supervisor/worker loop, durable state, honest correctness and benchmark publication, a Rust core crate, and a CPython-facing extension boundary. The implementation itself is real but still narrow. The published slice currently reports `364` cases across `50` manifests, with all `364` passing after `RBR-0170` converted the first alternation-heavy empty-yes-arm conditional pack into real Rust-backed behavior. The benchmark surface still reports `303` workloads with `253` real `rebar` timings and `50` explicit gaps after `RBR-0168` separated the alternation-heavy empty-arm benchmark anchors. The next queued work is `RBR-0171` through `RBR-0174` for empty-yes-arm benchmark catch-up and the alternation-bearing fully-empty follow-ons, with `RBR-0175` through `RBR-0180` already queued behind them for quantified omitted-no-arm and explicit-empty-else conditionals.

The practical read is simple: infrastructure is no longer the blocker, and compatibility work is progressing in small Rust-backed slices. The deterministic systematic corpus, the bounded nested empty-yes-arm and fully-empty conditional slices, both bounded quantified empty-arm conditional slices, and the first alternation-heavy empty-yes-arm conditional slice are now part of the tracked Rust-backed baseline. Near-term work is `RBR-0171` through `RBR-0174`, with `RBR-0175` through `RBR-0180` already queued behind them so the conditional frontier can continue through alternation-bearing fully-empty and quantified omitted-no-arm/explicit-empty-else follow-ons without another supervisor-only rewrite.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is a slice-health signal, not an end-state signal. `364` passes with `0` honest gaps across `364` published cases in `50` manifests means the currently published slice is caught up for what it covers, not that the project is close to replacing stdlib `re` across the board. The next queued work is `RBR-0171` through `RBR-0174` for alternation-heavy empty-yes-arm benchmark catch-up and the fully-empty follow-ons, with quantified omitted-no-arm and explicit-empty-else follow-ons already queued immediately behind them.

The benchmark report is still a coverage-first artifact too. It already exercises a wide workload set, but `50` workloads are still explicit gaps and the main published run still measures the source-tree shim rather than the fully built-native path. That is enough to guide the queue, but not enough to make broad speed claims yet.

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
