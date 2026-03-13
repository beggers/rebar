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
| Work queue | `8` ready, `0` in progress, `184` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `380` |
| Passing in published slice | `380` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `52` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, the published slice is expanding with explicit honest gaps and catch-up tasks, and overall stdlib-parity progress is still in the early implementation stage._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `309` |
| Workloads with real `rebar` timings | `261` |
| Known-gap workloads | `48` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `261` of `309` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0176` through `RBR-0180` for the bounded quantified omitted-no-arm parity work plus the quantified explicit-empty-else conditional follow-ons already anchored in the benchmark manifests.
- Then land `RBR-0181` through `RBR-0183` for one bounded nested two-arm conditional composition slice anchored to the remaining `conditional_group_exists_boundary` gap row.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Local git history is diverged from `origin/main`, so the loop cannot auto-push until the remote-only `USER-ASK-4` and `USER-ASK-5` commits are reconciled.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` now has the hard part of the operating system in place: a supervisor/worker loop, durable state, honest correctness and benchmark publication, a Rust core crate, and a CPython-facing extension boundary. The implementation itself is real but still narrow. The published correctness slice now reports `380` cases across `52` manifests with `372` passes and `8` explicit honest gaps after `RBR-0175` published the first bounded quantified omitted-no-arm conditional correctness pack. The benchmark surface still reports `309` workloads with `261` real `rebar` timings and `48` explicit gaps after `RBR-0174` caught that fully-empty alternation slice up on the published benchmark surface. The active ready queue now starts at `RBR-0176` for quantified omitted-no-arm parity, keeps `RBR-0177` through `RBR-0180` on quantified omitted-no-arm and explicit-empty-else catch-up, and already has `RBR-0181` through `RBR-0183` queued for one bounded nested two-arm conditional composition slice.

The practical read is simple: infrastructure is no longer the blocker, and compatibility work is progressing in small Rust-backed slices. The deterministic systematic corpus, the bounded nested empty-yes-arm and fully-empty conditional slices, both bounded quantified empty-arm conditional slices, the alternation-heavy empty-yes-arm conditional slice, and the alternation-bearing fully-empty conditional slice are already part of the tracked Rust-backed baseline and published benchmark surface. Quantified omitted-no-arm correctness publication has now reached the public scorecard, and Rust-backed parity plus benchmark catch-up for that slice, quantified explicit-empty-else follow-ons, and the first bounded nested two-arm conditional composition slice are next.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is a slice-health signal, not an end-state signal. `372` passes with `8` published honest gaps across `380` cases in `52` manifests means the scorecard has widened ahead of implementation again by one bounded quantified omitted-no-arm slice, not that the project is close to replacing stdlib `re` across the board. The immediate queue is `RBR-0176` through `RBR-0180` for quantified omitted-no-arm parity and quantified explicit-empty-else follow-ons, with one bounded nested two-arm conditional composition slice already queued behind them.

The benchmark report is still a coverage-first artifact too. It already exercises a wide workload set, but `48` workloads are still explicit gaps and the main published run still measures the source-tree shim rather than the fully built-native path. That is enough to guide the queue, but not enough to make broad speed claims yet.

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
