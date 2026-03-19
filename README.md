# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published frontier: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | Published correctness is 1326/1326 cases across 111 manifests with 0 honest gaps; the benchmark publication is 739/739 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice. |
| Current milestone | `RBR-0659` should catch the broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair up on the existing `benchmarks/workloads/nested_group_replacement_boundary.py` surface, so the shared replacement benchmark owner grows from `36` total / `36` measured / `0` known-gap workloads to `40` / `40` / `0` and the published source-tree benchmark report can move from `739` total / `739` measured / `0` known gaps to `743` / `743` / `0` across the same `30` manifests. |
| Work queue | `1` ready, `0` in progress, `658` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1326` |
| Passing in published slice | `1326` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: Published correctness is 1326/1326 cases across 111 manifests with 0 honest gaps; the benchmark publication is 739/739 measured workloads across 30 manifests with 0 known gaps, but it still runs through the source-tree shim on a bounded slice._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `739` |
| Workloads with real `rebar` timings | `739` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- `RBR-0659`: catch the broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair up on `benchmarks/workloads/nested_group_replacement_boundary.py`, moving that shared benchmark owner from `36` total / `36` measured / `0` known-gap workloads to `40` / `40` / `0` and the published source-tree benchmark surface from `739` / `739` / `0` to `743` / `743` / `0`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 739 workloads, so zero known gaps does not yet imply broad performance coverage.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. The current published correctness slice is fully green, but it is still a bounded frontier rather than a claim of broad drop-in `re` parity. The next bounded follow-on is benchmark catch-up for the broader `{1,4}` nested grouped-alternation plus branch-local-backreference replacement-template bytes pair.

The clearest benchmark signal worth trusting is still the tiny parser compile-proxy slice, where 8 parser workloads are 2.7921x faster on median than CPython. The broader module-facing publication still runs through the source-tree shim and sits at 0.0787x median, so it is methodology and coverage signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
