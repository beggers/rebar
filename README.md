# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 997 cases across 111 manifests, with 997 passing, 0 explicit failures, and 0 current `unimplemented` gaps; the main benchmark report covers 588 workloads with 588 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so this tracked slice is fully passing but the project remains far from drop-in `re` parity. |
| Current milestone | After ready `RBR-0510` drains, the surviving frontier is `RBR-0512`: catch the same broader `{1,4}` bytes grouped-conditional pair up on the existing `benchmarks/workloads/wider_ranged_repeat_quantified_group_boundary.py` path by adding the six bytes mirrors of the current `str` compile/search/fullmatch rows for `a((bc|de){1,4})?(?(1)d|e)` and `a(?P<outer>(bc|de){1,4})?(?(outer)d|e)` before broader bytes follow-ons reopen that family. |
| Work queue | `0` ready, `0` in progress, `511` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `997` |
| Passing in published slice | `997` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 997 cases across 111 manifests, with 997 passing, 0 explicit failures, and 0 current `unimplemented` gaps; the main benchmark report covers 588 workloads with 588 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so this tracked slice is fully passing but the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `588` |
| Workloads with real `rebar` timings | `588` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- With the ready queue drained, the surviving frontier is `RBR-0512`: add the six bytes mirrors for the broader `{1,4}` grouped-conditional benchmark rows on the existing `wider_ranged_repeat_quantified_group_boundary.py` path.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 588 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The published correctness slice now covers 997 cases across 111 manifests, with 997 passing, 0 explicit failures, and 0 current `unimplemented` gaps, and the benchmark publication covers 588 workloads with 588 real `rebar` timings and no explicit source-tree known gaps. The ready queue is empty, and backlog now points to `RBR-0512` as the next benchmark catch-up follow-on for that same bytes grouped-conditional pair.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice, where the published parser family is about 2.8x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
