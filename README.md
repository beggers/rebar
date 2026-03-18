# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1244 cases across 111 manifests, with 1244 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 704 workloads across 30 manifests with 704 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the tracked slice now fully passes but remains bounded and is not yet a near-full parity or native-path performance signal. |
| Current milestone | `RBR-0605` should catch the quantified nested-group alternation branch-local-backreference bytes pair up on the existing nested-group alternation benchmark surface by updating `benchmarks/workloads/nested_group_alternation_boundary.py`, `tests/benchmarks/benchmark_expectations.py`, `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `reports/benchmarks/latest.py`, so `nested-group-alternation-boundary` can move from `22` total workloads / `22` measured workloads / `0` known gaps to `25` / `25` / `0` and the combined benchmark report can move from `704` total workloads / `704` measured workloads / `0` known gaps to `707` / `707` / `0` without widening beyond the three numbered and named bytes mirrors of the already-published quantified nested-group branch-local-backreference rows. |
| Work queue | `1` ready, `0` in progress, `604` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1244` |
| Passing in published slice | `1244` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1244 cases across 111 manifests, with 1244 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 704 workloads across 30 manifests with 704 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the tracked slice now fully passes but remains bounded and is not yet a near-full parity or native-path performance signal._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `704` |
| Workloads with real `rebar` timings | `704` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0605` should add the three bytes benchmark mirrors for the newly landed quantified nested-group alternation branch-local-backreference pair, moving the combined benchmark report from `704 / 704 / 0` to `707 / 707 / 0` before broader benchmark follow-ons resume.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 704 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is still a bounded slice rather than near-full `re` parity, and the immediate queue is catching the newly landed quantified nested-group alternation branch-local-backreference bytes pair up on the published benchmark surface before broader benchmark follow-ons resume.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where 8 workloads are about 2.9x faster on median than CPython. Outside that slice, the main published benchmark report still runs through the source-tree shim and is slower overall, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
