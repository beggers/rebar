# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The status block below is the published slice: what passes today, how much of it is benchmarked, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, landing correctness first and Python-path benchmark catch-up immediately behind it. |
| Delivery estimate | The published correctness slice now covers 967 cases across 107 manifests, and all 967 currently pass; the main benchmark report covers 588 workloads with 581 real `rebar` timings and 7 explicit known gaps through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | The concrete surviving follow-on is `RBR-0489`, which should publish the exact nested grouped-alternation replacement-template pair already anchored on `grouped-alternation-replacement-boundary` by adding the two workflows `rebar.sub("a((b|c))d", "\\1x", "abdacd")` and `rebar.compile("a(?P<outer>(b|c))d").subn("\\g<outer>x", "acdabd", 1)` to the correctness surface so that pair stops existing only as benchmark-only debt and instead publishes as honest correctness coverage. |
| Work queue | `1` ready, `0` in progress, `488` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `967` |
| Passing in published slice | `967` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `107` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The published correctness slice now covers 967 cases across 107 manifests, and all 967 currently pass; the main benchmark report covers 588 workloads with 581 real `rebar` timings and 7 explicit known gaps through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `588` |
| Workloads with real `rebar` timings | `581` |
| Known-gap workloads | `7` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `581` of `588` published workloads have real `rebar` timings._

### Immediate Next Steps

- The ready-head task is `RBR-0489`, which should publish the exact nested grouped-alternation replacement-template pair already anchored on `grouped-alternation-replacement-boundary` so that pair stops existing only as benchmark-only debt and instead appears on the correctness surface.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded at 588 workloads and carries 7 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has the pieces that matter for the next phase: a Rust regex core, a CPython-facing extension boundary, and published correctness and benchmark scorecards. What it does not have yet is breadth. The published correctness slice now covers 967 cases across 107 manifests, and all 967 currently pass, but that slice is still narrow, and the benchmark publication is still bounded at 588 workloads with 7 explicit source-tree known gaps. The only ready task is `RBR-0489`, which should publish the exact nested grouped-alternation replacement-template pair already anchored on `grouped-alternation-replacement-boundary` so that pair becomes visible on the correctness surface.

The benchmark story is similarly early. The only clear positive speed signal today is the tiny parser compile slice, where the published parser family is about 2.7x faster on median than CPython. The much larger module-path publication still runs through the source-tree shim and is slower overall, so that result is useful signal rather than a general speed claim.

## Where To Look

Start with the tracked scorecards in `reports/correctness/latest.py` and `reports/benchmarks/latest.py`.

To rerun the same repo-local parity and benchmark harnesses from a checkout, use:

```bash
PYTHONPATH=python python3 -m rebar_harness.correctness --report <path>
PYTHONPATH=python python3 -m rebar_harness.benchmarks --report <path>
```

For stricter built-native benchmark spot checks, run `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-smoke --report <path>` or `PYTHONPATH=python python3 -m rebar_harness.benchmarks --native-full --report <path>`. `ops/state/current_status.md` tracks the current frontier; `ops/README.md` is only for loop and queue operations.
