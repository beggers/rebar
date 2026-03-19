# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1310 cases across 110 manifests, with 1302 passing, 0 explicit failures, and 8 honest gaps; the main benchmark report covers 731 workloads across 30 manifests with 731 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is still bounded and not yet a native-path performance signal. |
| Current milestone | `RBR-0645` should convert the broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair published by `RBR-0643` on `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, `python/rebar/__init__.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `reports/correctness/latest.py`, so `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-replacement-workflows` moves from `16` total / `8` passed / `8` `unimplemented` with mixed `str`/`bytes` coverage to `16` total / `16` passed / `0` `unimplemented`, and the combined correctness report moves from `1310` total / `1302` passed / `8` `unimplemented` across `110` manifests to `1310` total / `1310` passed / `0` `unimplemented` across the same `110` manifests. |
| Work queue | `1` ready, `0` in progress, `644` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1310` |
| Passing in published slice | `1302` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `8` |
| Covered manifests | `110` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1310 cases across 110 manifests, with 1302 passing, 0 explicit failures, and 8 honest gaps; the main benchmark report covers 731 workloads across 30 manifests with 731 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is still bounded and not yet a native-path performance signal._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `731` |
| Workloads with real `rebar` timings | `731` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0645`: convert the eight published bytes replacement-template rows for the broader `{2,}` nested grouped-alternation plus branch-local-backreference slice from `unimplemented` to Rust-backed passes, moving `reports/correctness/latest.py` from `1310` total / `1302` passed / `8` `unimplemented` to `1310` / `1310` / `0`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 731 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is mostly green inside its tracked slice but still carries eight honest bytes gaps, and that slice is still bounded rather than near-full `re` parity. The live queue front, `RBR-0645`, is the parity follow-on that would close those published gaps on the broader `{2,}` nested-group alternation plus branch-local-backreference replacement surface.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where the 8 parser workloads are 2.8483x faster on median than CPython. The broader module-facing publication still runs through the source-tree shim and sits at 0.0787x median, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
