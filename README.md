# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

Start with the status block for the current published slice, how much of it is measured, and what still blocks broader parity or performance claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is focused on expanding a still-bounded Rust-backed `re` subset while keeping the correctness and benchmark publications caught up with each newly supported slice. |
| Delivery estimate | Early subset, still far from drop-in parity: the Rust boundary covers literals, captures, several bounded conditional and replacement workflows, quantified branch-local backreferences, and grouped alternation through bounded `{1,4}` plus open-ended `{1,}` and `{2,}` counted-repeat slices. The last grouped slice aligned across correctness, Rust-backed parity, and the main Python-path benchmark surface remains quantified nested-group replacement-template workflows on `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d`; `RBR-0313` has already converted the adjacent quantified nested-group callable replacement slice to Rust-backed parity, `RBR-0316` is queued to catch that same bounded callback workflow up on the existing Python-path benchmark surface, and `RBR-0318` is seeded immediately behind it to reopen correctness on quantified nested-group alternation for `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`. |
| Current milestone | Milestone 2 now has quantified nested-group callable replacement at Rust-backed parity; `RBR-0316` is next to catch that bounded slice up on the existing Python-path benchmark surface, and `RBR-0318` is queued immediately behind it to reopen correctness on quantified nested-group alternation through the existing nested alternation path. |
| Work queue | `1` ready, `0` in progress, `321` done, `0` blocked |
| Foundation tracks | `0/0` landed (`[..................] 0%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `787` |
| Passing in published slice | `787` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `87` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Early subset, still far from drop-in parity: the Rust boundary covers literals, captures, several bounded conditional and replacement workflows, quantified branch-local backreferences, and grouped alternation through bounded `{1,4}` plus open-ended `{1,}` and `{2,}` counted-repeat slices. The last grouped slice aligned across correctness, Rust-backed parity, and the main Python-path benchmark surface remains quantified nested-group replacement-template workflows on `a((bc)+)d` and `a(?P<outer>(?P<inner>bc)+)d`; `RBR-0313` has already converted the adjacent quantified nested-group callable replacement slice to Rust-backed parity, `RBR-0316` is queued to catch that same bounded callback workflow up on the existing Python-path benchmark surface, and `RBR-0318` is seeded immediately behind it to reopen correctness on quantified nested-group alternation for `a((b|c)+)d` and `a(?P<outer>(?P<inner>b|c)+)d`._

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

- Land `RBR-0316` so the published quantified nested-group callable replacement slice reaches the existing Python-path benchmark surface.
- Follow it with `RBR-0318` so quantified nested-group alternation reopens on the correctness surface before broader counted repeats or deeper nested grouped execution broaden the queue.

### Current Risks

- The primary published benchmark report still measures the source-tree shim rather than the built-native extension path, so full-suite timing claims can still drift away from the verified native import boundary.
- The published benchmark surface still trails the Rust-backed quantified nested-group callable slice and carries 30 explicit known-gap workloads, so the scorecards remain bounded frontier reporting while `RBR-0318` waits immediately behind `RBR-0316`.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The safest read today is that correctness is ahead of the broader benchmark story, the main published benchmark report still runs through the source-tree shim, and the project is still advancing one bounded grouped slice at a time rather than closing in on broad `re` parity. The only speed signal worth quoting is the tiny parser/compile slice, where eight published parser workloads median about 2.1x CPython; the much larger module-path report is still slower overall and not a basis for broad performance claims.

## Where To Look

For the published scorecards, start with `reports/correctness/latest.json` and `reports/benchmarks/latest.json`. For the latest strict built-native checkpoints, use `reports/benchmarks/native_full.json` and `reports/benchmarks/native_smoke.json`. For the broader project frontier, `ops/state/current_status.md` is the current narrative state; `ops/README.md` is the operator guide for the loop and queue layout.

## Inspecting The Current Slice

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
```

Loop-running and queue-management details stay in `ops/README.md` so this landing page can stay focused on project shape, current coverage, and the published reports.
