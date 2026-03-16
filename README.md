# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 963 cases across 107 manifests, with 963 passes, 0 failures, and 0 published correctness gaps; the main benchmark report still covers 588 workloads with 573 real `rebar` timings through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | With `RBR-0471` already queued at the ready head, the concrete surviving follow-on after that likely drain is `RBR-0473`, which should republish the exact `IGNORECASE|ASCII` literal benchmark pair on `literal-flag-boundary` as measured source-tree timings. |
| Work queue | `1` ready, `0` in progress, `472` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `963` |
| Passing in published slice | `963` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `107` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 963 cases across 107 manifests, with 963 passes, 0 failures, and 0 published correctness gaps; the main benchmark report still covers 588 workloads with 573 real `rebar` timings through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `588` |
| Workloads with real `rebar` timings | `573` |
| Known-gap workloads | `15` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `573` of `588` published workloads have real `rebar` timings._

### Immediate Next Steps

- The concrete ready-head follow-on is `RBR-0473`, which should republish the exact `module-search-ignorecase-ascii-cold-gap` / `pattern-search-ignorecase-ascii-warm-gap` pair on `literal-flag-boundary` as measured source-tree timings so benchmark coverage catches up to the now-zero-gap `IGNORECASE|ASCII` literal slice.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 588 workloads and carries 15 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The published correctness slice is now fully passing at 963 of 963 cases across 107 manifests, but the benchmark publication is still bounded at 588 workloads with 15 explicit source-tree known gaps. The immediate follow-on is `RBR-0473`, which catches the paired `IGNORECASE|ASCII` literal benchmark rows up to that now-zero-gap correctness boundary.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice, where the published parser family is about 2.9x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
