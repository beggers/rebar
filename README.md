# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1294 cases across 110 manifests, with 1294 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 727 workloads across 30 manifests with 727 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is broader and now green inside that slice, but it is still bounded and not yet a native-path performance signal. |
| Current milestone | `RBR-0637` should add the eight bytes callable-replacement counterparts for the broader-range open-ended `{2,}` nested grouped-alternation plus branch-local-backreference slice on `tests/conformance/fixtures/nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py`, `tests/python/test_callable_replacement_parity_suite.py`, `tests/conformance/correctness_expectations.py`, and `reports/correctness/latest.py`, so `nested-broader-range-open-ended-quantified-group-alternation-branch-local-backreference-callable-replacement-workflows` moves from `8` total / `8` passed / `0` unimplemented with `['str']` coverage to `16` total with mixed `str`/`bytes` coverage and the combined correctness report moves from `1294` total cases across `110` manifests to `1302` across `110` manifests while reporting the new bytes rows honestly as passes or `unimplemented` on the shared callable surface. |
| Work queue | `1` ready, `0` in progress, `636` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1294` |
| Passing in published slice | `1294` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `110` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1294 cases across 110 manifests, with 1294 passing, 0 explicit failures, and 0 honest gaps; the main benchmark report covers 727 workloads across 30 manifests with 727 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is broader and now green inside that slice, but it is still bounded and not yet a native-path performance signal._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `727` |
| Workloads with real `rebar` timings | `727` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0637`: publish the bytes callable-replacement correctness pair for the adjacent broader `{2,}` nested grouped-alternation plus branch-local-backreference slice, moving the published correctness report from `1294` to `1302` total cases while reporting the new bytes rows honestly as passes or `unimplemented`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 727 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is still a bounded slice rather than near-full `re` parity, but it is now green inside that slice: 1294 published cases across 110 manifests, all passing. The live queue front, `RBR-0637`, reopens correctness on the adjacent bytes callable-replacement slice for the same broader `{2,}` nested-group frontier.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where 8 workloads are 2.935x faster on median than CPython. Outside that slice, the broader module-facing publication is still a source-tree-shim result, with 719 workloads running at 0.0767x of CPython on median, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
