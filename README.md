# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 1094 cases across 111 manifests, with 1080 passing, 0 explicit failures, and 14 honest gaps; the main benchmark report covers 632 workloads across 30 manifests with 632 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the project is broader again but still clearly partial. |
| Current milestone | After ready `RBR-0535` drains, the surviving frontier is `RBR-0537`: convert the broader-range open-ended `{2,}` grouped-alternation-plus-conditional bytes pair to real parity on the existing correctness/parity path so `broader-range-open-ended-quantified-group-alternation-conditional-workflows` moves from `28` total / `14` passed / `14` unimplemented to `28` / `28` / `0` and the combined correctness report moves from `1094` / `1080` / `14` to `1094` / `1094` / `0` before bytes benchmark catch-up widens that broader-range family. |
| Work queue | `0` ready, `0` in progress, `536` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `1094` |
| Passing in published slice | `1080` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `14` |
| Covered manifests | `111` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 1094 cases across 111 manifests, with 1080 passing, 0 explicit failures, and 14 honest gaps; the main benchmark report covers 632 workloads across 30 manifests with 632 real `rebar` timings and 0 explicit known gaps through the source-tree shim, so the project is broader again but still clearly partial._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `632` |
| Workloads with real `rebar` timings | `632` |
| Known-gap workloads | `0` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

### Immediate Next Steps

- With the queue drained, the surviving frontier is `RBR-0537`: convert the broader-range open-ended `{2,}` grouped-alternation-plus-conditional bytes pair to real parity so the combined report moves from `1094` / `1080` / `14` to `1094` / `1094` / `0`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 632 workloads even though the report no longer carries explicit known-gap rows.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The current published correctness slice spans 1094 cases across 111 manifests, with 1080 already passing and 14 honest gaps concentrated in the just-published broader-range open-ended `{2,}` grouped-alternation-plus-conditional bytes pair. That still represents a narrow tracked frontier rather than near-full stdlib `re` parity. With the queue drained, the surviving follow-on is `RBR-0537`, which converts that same bytes pair to real parity. The main benchmark report spans 632 workloads through the source-tree shim.

The benchmark story is similarly early. The clearest positive speed signal today is still the tiny parser compile slice, where the 8 published parser workloads are about 2.6x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
