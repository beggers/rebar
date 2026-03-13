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
| Work queue | `10` ready, `0` in progress, `165` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `330` |
| Passing in published slice | `330` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `46` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, the published slice is expanding with explicit honest gaps and catch-up tasks, and overall stdlib-parity progress is still in the early implementation stage._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `296` |
| Workloads with real `rebar` timings | `243` |
| Known-gap workloads | `53` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `243` of `296` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0158` through `RBR-0161` for nested empty-yes-arm benchmark catch-up plus the bounded nested fully-empty publication/parity/benchmark slice.
- Then land `RBR-0162` through `RBR-0168` for quantified empty-arm follow-ons plus the alternation-heavy empty-arm anchor cleanup that reopens the broader queue.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Local git history is diverged from `origin/main`, so the loop cannot auto-push until the remote-only `USER-ASK-4` and `USER-ASK-5` commits are reconciled.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` now has the hard part of the operating system in place: a supervisor/worker loop, durable state, honest correctness and benchmark publication, a Rust core crate, and a CPython-facing extension boundary. The implementation itself is real but still narrow. The published slice currently reports `330` passes with `0` honest gaps across `330` cases in `46` manifests, with the latest frontier widened through one bounded nested empty-yes-arm conditional slice rather than through broad parser or engine coverage.

The practical read is simple: infrastructure is no longer the blocker, and compatibility work is progressing in small Rust-backed slices. The deterministic systematic corpus and the bounded nested empty-yes-arm conditional slice are now part of the Rust-backed published baseline, and near-term work is about benchmark catch-up for that slice, then landing the nested fully-empty publication/parity/benchmark trio, then the quantified empty-arm follow-ons, and then the queued alternation-heavy empty-arm anchor cleanup that reopens the next broader slice.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is a slice-health signal, not an end-state signal. `330` passes with `0` honest gaps across `330` published cases in `46` manifests means the currently tracked frontier is internally green for the published slice, not that the project is close to replacing stdlib `re` across the board. The next queued work is widening that frontier again, starting with benchmark publication for the newly landed nested empty-yes-arm slice and then one bounded nested fully-empty follow-on.

The benchmark report is still a coverage-first artifact too. It already exercises a wide workload set, but 54 rows are still explicit gaps and the main published run still measures the source-tree shim rather than the fully built-native path. That is enough to guide the queue, but not enough to make broad speed claims yet.

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
