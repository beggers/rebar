# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness report now covers 1244 cases across 111 manifests, with 1234 passing, 0 explicit failures, and 10 honest gaps; the main benchmark report covers 704 workloads across 30 manifests with 704 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is wider but still bounded and not yet a near-full parity or native-path performance signal. |
| Current milestone | `RBR-0603` should convert the quantified nested-group alternation branch-local-backreference bytes pair behind `rebar._rebar` on the existing branch-local parity surface by updating `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, `python/rebar/__init__.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `reports/correctness/latest.py`, so `match.quantified_nested_group_alternation_branch_local_backreference` can move from `20` total / `10` passed / `10` unimplemented with mixed `str`/`bytes` coverage to `20` / `20` / `0`, and the combined correctness report can move from `1244` total / `1234` passed / `10` unimplemented across `111` manifests to `1244` / `1244` / `0` without widening beyond the exact ten numbered and named bytes mirrors that `RBR-0601` publishes on the shared branch-local parity suite. |
| Work queue | `1` ready, `0` in progress, `602` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1244` |
| Passing in published slice | `1234` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `10` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness report now covers 1244 cases across 111 manifests, with 1234 passing, 0 explicit failures, and 10 honest gaps; the main benchmark report covers 704 workloads across 30 manifests with 704 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the published slice is wider but still bounded and not yet a near-full parity or native-path performance signal._

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

- `RBR-0603` should convert the quantified nested-group alternation branch-local-backreference bytes pair from honest correctness gaps into real parity, moving the combined scorecard from `1244 / 1234 / 10` to `1244 / 1244 / 0` before benchmark follow-ons resume.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 704 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is still a bounded slice rather than near-full `re` parity, and the immediate queue is converting the newly published quantified nested-group alternation branch-local-backreference bytes pair from honest gaps into real parity before broader benchmark catch-up resumes.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where 8 workloads are about 2.9x faster on median than CPython. Outside that slice, the main published benchmark report still runs through the source-tree shim and is slower overall, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
