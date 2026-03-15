# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now passes end to end, but it is still narrow and the main benchmark report still runs through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | Milestone 2 now has `RBR-0378` seeded as the surviving follow-on so, once `RBR-0376` catches the explicit open-ended `{1,}` nested-group alternation plus branch-local-backreference callable-replacement workflows for `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` up on the Python-path benchmark surface, the same nested-group branch-local-backreference frontier reopens on replacement-template publication for those forms before replacement-template parity, replacement-template benchmark catch-up, broader callback semantics, or deeper nested grouped execution broaden the queue. |
| Work queue | `1` ready, `0` in progress, `380` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `873` |
| Passing in published slice | `873` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `97` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now passes end to end, but it is still narrow and the main benchmark report still runs through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `533` |
| Workloads with real `rebar` timings | `509` |
| Known-gap workloads | `24` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `509` of `533` published workloads have real `rebar` timings._

### Immediate Next Steps

- Keep `RBR-0378` queued so, once `RBR-0376` catches the explicit open-ended `{1,}` nested-group callable-replacement slice for `a((b|c){1,})\\2d` and `a(?P<outer>(?P<inner>b|c){1,})(?P=inner)d` up on the Python-path benchmark surface, the frontier reopens on replacement-template publication for those forms.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded and carries 24 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The current published correctness slice is still intentionally narrow, but it now passes end to end within that bounded surface. That is useful evidence that a real Rust-backed slice can close cleanly, not evidence of broad drop-in parity.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice: across eight published parser workloads it is about 2x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
