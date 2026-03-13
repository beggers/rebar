# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is widening a real Rust-backed subset one bounded regex slice at a time, and the project is still far from drop-in `re` parity. |
| Delivery estimate | Foundation work is complete, but the published Rust-backed slice is still narrow and the next milestone needs to be re-seeded now that the current grouped `{2,}` frontier and its benchmark-wrapper cleanup are landed. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `0` ready, `0` in progress, `265` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `677` |
| Passing in published slice | `677` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `79` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, but the published Rust-backed slice is still narrow and the next milestone needs to be re-seeded now that the current grouped `{2,}` frontier and its benchmark-wrapper cleanup are landed._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `452` |
| Workloads with real `rebar` timings | `419` |
| Known-gap workloads | `33` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `419` of `452` published workloads have real `rebar` timings._

### Immediate Next Steps

- Seed the next bounded milestone; the implementation queue is empty now that `RBR-0262` and the current grouped `{2,}` benchmark catch-up work landed on 2026-03-13.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Built-native benchmark results still live in separate sidecars with narrower workload coverage than the main published suite.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` is no longer just a harness scaffold. There is a real Rust core, a CPython-facing extension boundary, published correctness and benchmark reports, and a repeatable workflow for widening one bounded regex slice at a time.

The important caveat is still project shape, not raw counts: the published slice is internally clean, but it remains small relative to stdlib `re`. Benchmarking is also still in the qualification phase. The main published suite measures the source-tree shim, while built-native runs are published separately so the repo can distinguish "measured" from "ready to claim faster than CPython."

## Reading The Status Block

Treat the correctness numbers as "the current documented frontier is coherent," not as a claim of broad drop-in compatibility. Treat the benchmark numbers as coverage signals first; until the built-native path is the main published path, the README deliberately avoids headline speed claims.

## Where To Look

If you want the detailed project state, start with `ops/state/current_status.md` and `ops/state/backlog.md`. If you want the published scorecards, use `reports/correctness/latest.json`, `reports/benchmarks/latest.json`, `reports/benchmarks/native_full.json`, and `reports/benchmarks/native_smoke.json`. For the operating model and queue layout, `ops/README.md` is the canonical reference.

## Useful Commands

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
python3 scripts/rebar_ops.py render supervisor
python3 scripts/rebar_ops.py cycle --force-agent feature-implementation
python3 scripts/rebar_ops.py cycle --force-supervisor
bash scripts/loop_forever.sh
```

## Operating Notes

- Run the forever loop from a normal shell on a writable checkout.
- Do not start a second `python3 scripts/rebar_ops.py cycle ...` run against the same checkout while `scripts/loop_forever.sh` is active.
- Avoid launching the loop from inside another sandboxed Codex session; nested sandboxes can distort child-agent behavior and cache writes.
