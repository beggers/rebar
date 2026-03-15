# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 917 cases with 917 passing and 0 honest `unimplemented` outcomes, and the main benchmark report now covers 554 workloads with 530 real `rebar` timings, but it still runs through the source-tree shim with 24 explicit gaps, so the project remains far from drop-in `re` parity. |
| Current milestone | Milestone 2 now stays on the bounded broader-range open-ended `{2,}` nested-group alternation plus branch-local-backreference conditional slice for `a((b|c){2,})\2(?(2)d|e)` and `a(?P<outer>(?P<inner>b|c){2,})(?P=inner)(?(inner)d|e)`; after `RBR-0404` closes the Python-path benchmark gap on `benchmarks/workloads/branch_local_backreference_boundary.py`, the surviving concrete follow-on is correctness-publication task `RBR-0406` for the same numbered and named pattern pair through replacement-template `sub()` / `subn()` workflows. |
| Work queue | `0` ready, `0` in progress, `408` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `917` |
| Passing in published slice | `917` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `102` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 917 cases with 917 passing and 0 honest `unimplemented` outcomes, and the main benchmark report now covers 554 workloads with 530 real `rebar` timings, but it still runs through the source-tree shim with 24 explicit gaps, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `554` |
| Workloads with real `rebar` timings | `530` |
| Known-gap workloads | `24` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `530` of `554` published workloads have real `rebar` timings._

### Immediate Next Steps

- The surviving ready follow-on is correctness-publication task `RBR-0406` for the broader-range open-ended `{2,}` nested-group branch-local-backreference conditional replacement-template `sub()` / `subn()` slice.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 554 workloads and carries 24 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The current published correctness slice is still intentionally narrow, even though the latest publication now passes all 917 cases in that tracked slice. That is useful evidence that the project can close one bounded frontier at a time, not evidence of broad drop-in parity.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice: across eight published parser workloads it is about 2x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
