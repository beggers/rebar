# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | Published parity is 1310/1318 cases across 111 manifests with 8 honest gaps; the benchmark publication is 735/735 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice. |
| Current milestone | `RBR-0651` should turn the broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template `str` rows on the shared replacement path in `crates/rebar-core/src/lib.rs`, `crates/rebar-cpython/src/lib.rs`, `python/rebar/__init__.py`, `tests/python/test_fixture_backed_replacement_parity_suite.py`, and `reports/correctness/latest.py` into real Rust-backed parity, so the expanded combined report moves from `1318` total / `1310` passed / `8` `unimplemented` across `111` manifests to `1318` / `1318` / `0` while keeping that slice on the ordinary replacement surface before later Python-path benchmark catch-up reopens the family. |
| Work queue | `1` ready, `0` in progress, `650` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1318` |
| Passing in published slice | `1310` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `8` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: Published parity is 1310/1318 cases across 111 manifests with 8 honest gaps; the benchmark publication is 735/735 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `735` |
| Workloads with real `rebar` timings | `735` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0651`: convert the newly published broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template `str` slice to real parity on the shared replacement surface, moving the expanded correctness report from `1318` total / `1310` passed / `8` `unimplemented` across `111` manifests to `1318` / `1318` / `0`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 735 workloads, so zero known gaps does not yet imply broad performance coverage.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current publication is still narrow and no longer fully green after the latest broader `{1,4}` nested replacement-template publication: 1310 of 1318 cases pass, with 8 honest gaps. The next bounded follow-on is `RBR-0651`, which converts that slice to real parity on the shared replacement surface.

The benchmark story is similarly early. The clearest trustworthy positive signal today is still the tiny parser compile-proxy slice, where the 8 parser workloads are 2.7302x faster on median than CPython. The broader module-facing publication still runs through the source-tree shim and sits at 0.0754x median, so it is methodology signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
