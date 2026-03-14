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
| Current milestone | Milestone 2 now has quantified nested-group callable replacement at Rust-backed parity; `RBR-0316` is next to catch that bounded slice up on the existing Python-path benchmark surface, and `RBR-0318` is queued immediately behind it to reopen correctness on quantified nested-group alternation through the existing nested alternation path. |
| Work queue | `1` ready, `0` in progress, `320` done, `0` blocked |
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
| Baseline | CPython 3.12.3 (module `re`, exe `/home/ubuntu/rebar/.venv/bin/python`) |
| Published workloads | `499` |
| Workloads with real `rebar` timings | `470` |
| Known-gap workloads | `29` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `470` of `499` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0316` to catch the published quantified nested-group callable replacement slice up on the existing Python-path benchmark surface.
- Follow with `RBR-0318` to reopen correctness on quantified nested-group alternation through `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The published benchmark surface is still bounded and carries 30 explicit known-gap workloads, so the scorecards remain frontier reporting while quantified nested-group callable replacement still needs benchmark catch-up and quantified nested-group alternation sits immediately behind it.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The project is still moving one bounded slice at a time, so the status block and published reports are the place to read the exact frontier and measurement coverage. Near term, the frontier is quantified nested-group callable replacement on the correctness surface, then the same slice behind the Rust boundary. The one benchmark result worth surfacing here today is the tiny compile-path parser slice: its five currently measured workloads median about 2.2x CPython, while the much larger module-path report is still slower overall, still source-tree-shim-backed, and still not a basis for broad speed claims.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.json` and `reports/benchmarks/latest.json`. For the latest strict built-native checkpoints, use `reports/benchmarks/native_full.json` and `reports/benchmarks/native_smoke.json`. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
