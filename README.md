# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1278 cases across 111 manifests, with 1268 passing, 0 explicit failures, and 10 honest gaps; the main benchmark report covers 713 workloads across 30 manifests with 713 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the tracked slice is still bounded and not yet a near-full parity or native-path performance signal. |
| Current milestone | `RBR-0621` should convert the already-published bytes counterparts for the broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional pair behind `rebar._rebar` by updating `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, `python/rebar/__init__.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `reports/correctness/latest.py`, so `match.nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional` can move from `20` total / `10` passed / `10` `unimplemented` to `20` / `20` / `0` with mixed `str`/`bytes` coverage while the combined correctness report moves from `1278` / `1268` / `10` to `1278` / `1278` / `0` across `111` manifests without widening into bytes benchmarks or deeper grouped execution. |
| Work queue | `1` ready, `0` in progress, `620` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1278` |
| Passing in published slice | `1268` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `10` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1278 cases across 111 manifests, with 1268 passing, 0 explicit failures, and 10 honest gaps; the main benchmark report covers 713 workloads across 30 manifests with 713 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the tracked slice is still bounded and not yet a near-full parity or native-path performance signal._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `713` |
| Workloads with real `rebar` timings | `713` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0621` should convert the already-published bytes pair for the broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference conditional slice behind `rebar._rebar`, moving that manifest from `20 / 10 / 10` to `20 / 20 / 0` and the combined correctness report from `1278 / 1268 / 10` to `1278 / 1278 / 0` without widening into bytes benchmarks.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 713 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is still a bounded slice rather than near-full `re` parity; the live queue front, `RBR-0621`, is converting the already-published bytes follow-on for the broader-range open-ended `{2,}` conditional branch-local-backreference slice from honest gaps into real Rust-backed parity.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where 8 workloads are about 2.9x faster on median than CPython. Outside that slice, the main 713-workload published benchmark report still runs through the source-tree shim and is slower overall, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
