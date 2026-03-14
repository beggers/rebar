# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

Start with the status block for the current published slice, how much of it is measured, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 remains a bounded Rust-backed subset, with correctness, Rust-backed parity, and the main Python-path benchmark report aligned through quantified nested-group replacement templates. |
| Delivery estimate | The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity: the published slice is narrow, the main benchmark report still runs through the source-tree shim, and quantified nested-group callable replacement plus deeper grouped execution remain ahead. |
| Current milestone | Milestone 2 now has quantified nested-group callable replacement published on the correctness surface; `RBR-0313` is next to convert that bounded slice to Rust-backed parity, and `RBR-0316` is queued immediately behind it to catch the same slice up on the existing Python-path benchmark surface. |
| Work queue | `1` ready, `0` in progress, `318` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `787` |
| Passing in published slice | `787` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `87` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity: the published slice is narrow, the main benchmark report still runs through the source-tree shim, and quantified nested-group callable replacement plus deeper grouped execution remain ahead._

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

- Land `RBR-0313` to convert the published quantified nested-group callable replacement slice to Rust-backed parity.
- Follow with `RBR-0316` to catch that same bounded callable slice up on the existing Python-path benchmark surface.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded and carries 30 explicit known-gap workloads, so the scorecards remain frontier reporting while quantified nested-group callable replacement still needs Rust-backed parity and benchmark catch-up.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The project is still moving one bounded slice at a time, so the status block and published reports are the place to read the exact frontier and measurement coverage. Near term, the frontier is quantified nested-group callable replacement on the correctness surface, then the same slice behind the Rust boundary; broader benchmark catch-up and speed claims stay secondary.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.json` and `reports/benchmarks/latest.json`. For the latest strict built-native checkpoints, use `reports/benchmarks/native_full.json` and `reports/benchmarks/native_smoke.json`. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
