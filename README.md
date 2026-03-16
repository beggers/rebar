# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 949 cases across 106 manifests and is fully passing; the main benchmark report now covers 565 workloads with 542 real `rebar` timings through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | Milestone 2 stays on the bounded two-arm conditional replacement-template benchmark family for `a(b)?c(?(1)d|e)` and `a(?P<word>b)?c(?(word)d|e)`; the concrete surviving follow-on is `RBR-0433`, which should keep `benchmarks/workloads/conditional_group_exists_boundary.py` on that same family by adding the remaining absent-capture numbered `module.subn()` plus named compiled-`Pattern` `sub()` / `subn()` replacement-template timings already published on `tests/conformance/fixtures/conditional_group_exists_replacement_template_workflows.py`. |
| Work queue | `0` ready, `0` in progress, `432` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `949` |
| Passing in published slice | `949` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `106` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 949 cases across 106 manifests and is fully passing; the main benchmark report now covers 565 workloads with 542 real `rebar` timings through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `565` |
| Workloads with real `rebar` timings | `543` |
| Known-gap workloads | `22` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `543` of `565` published workloads have real `rebar` timings._

### Immediate Next Steps

- The concrete surviving follow-on is `RBR-0433`, which should keep `benchmarks/workloads/conditional_group_exists_boundary.py` on the bounded two-arm conditional replacement-template family by adding the remaining absent-capture numbered `module.subn()` plus named compiled-`Pattern` `sub()` / `subn()` replacement-template timings already published on the shared correctness path.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 565 workloads and carries 23 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The current correctness publication is fully passing on its 949-case slice, but that slice is still narrow enough that it should be read as evidence of steady parity work, not evidence of broad drop-in coverage.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice: across eight published parser workloads it is about 2x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
