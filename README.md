# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 965 cases across 107 manifests, with 963 passes, 0 failures, and 2 published correctness gaps; the main benchmark report still covers 588 workloads with 575 real `rebar` timings and 13 explicit known gaps through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | With `RBR-0475` already queued at the ready head, the concrete surviving follow-on after that likely drain is `RBR-0477`, which should convert the exact leading-capture grouped-segment search pair already being published on `grouped-segment-workflows` into real Rust-backed parity before the existing `grouped-named-boundary` benchmark gap rows are revisited. |
| Work queue | `1` ready, `0` in progress, `476` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `965` |
| Passing in published slice | `963` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `2` |
| Covered manifests | `107` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 965 cases across 107 manifests, with 963 passes, 0 failures, and 2 published correctness gaps; the main benchmark report still covers 588 workloads with 575 real `rebar` timings and 13 explicit known gaps through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `588` |
| Workloads with real `rebar` timings | `575` |
| Known-gap workloads | `13` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `575` of `588` published workloads have real `rebar` timings._

### Immediate Next Steps

- The ready-head task is `RBR-0477`, which should convert the grouped-segment leading-capture `(ab)c` module/pattern `search()` pair to real Rust-backed parity before the matching benchmark gap rows are republished as measured timings.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 588 workloads and carries 13 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The published correctness slice now passes 963 of 965 cases across 107 manifests, leaving two honest grouped-segment gaps, and the benchmark publication is still bounded at 588 workloads with 13 explicit source-tree known gaps. The only ready task is `RBR-0477`, which should convert that `(ab)c` leading-capture search pair to real parity before the matching benchmark gap rows are republished as measured timings.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice, where the published parser family is about 2.9x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
