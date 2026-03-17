# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 1080 cases across 111 manifests, with 1067 passing, 0 explicit failures, and 13 honest gaps; the main benchmark report covers 626 workloads across 30 manifests with 626 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the project is broader again but still clearly partial. |
| Current milestone | After ready `RBR-0532` drains, the surviving frontier is `RBR-0533`: convert the same open-ended `{1,}` grouped-alternation-plus-conditional bytes pair behind `rebar._rebar` on the existing open-ended parity surface so the reopened 13-case bytes slice returns the published correctness report to a gap-free `1080` passes before benchmark catch-up widens that family. |
| Work queue | `0` ready, `0` in progress, `532` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1080` |
| Passing in published slice | `1067` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `13` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 1080 cases across 111 manifests, with 1067 passing, 0 explicit failures, and 13 honest gaps; the main benchmark report covers 626 workloads across 30 manifests with 626 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the project is broader again but still clearly partial._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `626` |
| Workloads with real `rebar` timings | `626` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- With the queue drained, the surviving frontier is `RBR-0533`: convert the reopened 13-case open-ended grouped-alternation-plus-conditional bytes pair behind `rebar._rebar` and return the published correctness slice to `1080/1080` before bytes benchmark catch-up widens that family.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 626 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The current published correctness slice is still tightly bounded: 1067 of 1080 published cases pass across 111 manifests, with the remaining 13 `unimplemented` cases concentrated in the reopened open-ended grouped-alternation-plus-conditional bytes pair. With the queue drained, the surviving follow-on is `RBR-0533`, which should return that slice to `1080/1080` before bytes benchmark catch-up widens the family. The main benchmark report spans 626 workloads through the source-tree shim.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice, where the published parser family is about 2.9x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
