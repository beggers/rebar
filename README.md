# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

Start with the status block for the current published slice, how much of it is measured, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still a bounded Rust-backed subset: correctness and Rust-backed parity are aligned through quantified nested-group replacement templates, while the main Python-path benchmark report still trails that slice by one bounded follow-on and quantified nested-group callable replacement is queued immediately behind it. |
| Delivery estimate | The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity. Correctness and Rust-backed parity are aligned through quantified nested-group replacement templates, the main Python-path benchmark surface still trails that slice by one bounded follow-on, publication still runs through the source-tree shim, and broader callable-replacement plus deeper nested grouped execution work remain ahead. |
| Current milestone | Milestone 2 now has quantified nested-group replacement-template parity aligned on the correctness and Rust-backed surfaces; `RBR-0307` is next to catch that slice up on the main Python-path benchmark surface, and `RBR-0309` is queued immediately behind it to reopen quantified nested-group callable replacement on the correctness surface. |
| Work queue | `2` ready, `0` in progress, `311` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `779` |
| Passing in published slice | `779` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `86` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity. Correctness and Rust-backed parity are aligned through quantified nested-group replacement templates, the main Python-path benchmark surface still trails that slice by one bounded follow-on, publication still runs through the source-tree shim, and broader callable-replacement plus deeper nested grouped execution work remain ahead._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `496` |
| Workloads with real `rebar` timings | `466` |
| Known-gap workloads | `30` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `466` of `496` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0307` to catch quantified nested-group replacement benchmarks up on the main Python-path surface.
- Follow with `RBR-0309` to publish quantified nested-group callable replacement workflows on the correctness surface.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface still trails the parity-aligned quantified nested-group replacement slice and carries 30 explicit known-gap workloads, so the scorecards remain bounded frontier reporting.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The project is still moving one bounded slice at a time, so the status block and published reports are the place to read the exact frontier and measurement coverage. Near term, the work stays on benchmark catch-up and trustworthy Python-path reporting before broader compatibility or performance claims widen.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.json` and `reports/benchmarks/latest.json`. For the latest strict built-native checkpoints, use `reports/benchmarks/native_full.json` and `reports/benchmarks/native_smoke.json`. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
