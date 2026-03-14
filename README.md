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
| Current milestone | Milestone 2 now has `RBR-0328` seeded as the surviving follow-on so the bounded nested-group-alternation-plus-branch-local-backreference slice reaches the existing Python-path benchmark surface after the current `RBR-0326` parity task lands on `benchmarks/workloads/nested_group_alternation_boundary.py`. |
| Work queue | `1` ready, `0` in progress, `330` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `801` |
| Passing in published slice | `801` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `89` |
| Source | [`reports/correctness/latest.py`](reports/correctness/latest.py) |

_These correctness counts cover only the published slice. Overall delivery estimate: The repo now has real parity and benchmark publications, but they still cover a narrow subset and the main benchmark report still runs through the source-tree shim, so the project remains far from drop-in `re` parity._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `502` |
| Workloads with real `rebar` timings | `474` |
| Known-gap workloads | `28` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.py`](reports/benchmarks/latest.py) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native smoke and full-suite modes remain available for ad hoc runs and tests via `--native-smoke` and `--native-full` when you pass an explicit `--report` path._

_README speedup rollups stay omitted while only `474` of `502` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0328` after the current bounded nested-group-alternation-plus-branch-local-backreference parity task lands so the remaining `nested_group_alternation_boundary.py` gap turns into measured Python-path benchmark coverage.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded and carries 28 explicit known-gap workloads.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark publications. It is still a bounded `re` subset, not a drop-in replacement.

The published reports currently say three things: the implemented correctness slice is clean at the current frontier, the benchmark surface is still partial and source-tree-shim-backed, and the project is still moving one bounded regex shape at a time rather than closing in on broad `re` parity. The only speed signal worth repeating here is the tiny parser/compile slice, where the published median is about 2.0x CPython across eight workloads; the much larger module-path report is still slower overall and not a basis for broad performance claims.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.py` and `reports/benchmarks/latest.py`. For strict built-native coverage, run `python -m rebar_harness.benchmarks --native-smoke --report <path>` or `python -m rebar_harness.benchmarks --native-full --report <path>` when you need an ad hoc native-path scorecard. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
