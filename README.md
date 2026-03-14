# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

Start with the status block for the current published slice, how much of it is measured, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening one bounded Rust-backed regex slice at a time, keeping correctness and the published Python-path benchmark surface aligned at the current frontier. |
| Delivery estimate | The repo now has real parity and benchmark publications, but they still cover a narrow subset and the main benchmark report still runs through the source-tree shim, so the project remains far from drop-in `re` parity. |
| Current milestone | Milestone 2 now has quantified nested-group callable replacement aligned across correctness, Rust-backed parity, and the main Python-path benchmark surface, and quantified nested-group alternation is published on the correctness surface; `RBR-0322` is seeded as the surviving follow-on to catch that same bounded slice up on the main Python-path benchmark surface once the queued parity step clears. |
| Work queue | `2` ready, `0` in progress, `324` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `793` |
| Passing in published slice | `793` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `88` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: The repo now has real parity and benchmark publications, but they still cover a narrow subset and the main benchmark report still runs through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `499` |
| Workloads with real `rebar` timings | `470` |
| Known-gap workloads | `29` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `470` of `499` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0322` once the queued quantified nested-group alternation parity step clears so that same bounded slice reaches the main Python-path benchmark surface.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded and carries 29 explicit known-gap workloads, including the quantified nested-group alternation slice that still needs benchmark catch-up.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The safest read today is that correctness is ahead of the broader benchmark story, the main published benchmark report still runs through the source-tree shim, and the project is still advancing one bounded grouped slice at a time rather than closing in on broad `re` parity. The only speed signal worth quoting is the tiny parser/compile slice, where eight published parser workloads median about 2.1x CPython; the much larger module-path report is still slower overall and not a basis for broad performance claims.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.json` and `reports/benchmarks/latest.json`. For strict built-native coverage, run `python -m rebar_harness.benchmarks --native-smoke --report <path>` or `python -m rebar_harness.benchmarks --native-full --report <path>` when you need an ad hoc native-path scorecard. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
