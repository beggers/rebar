# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still widening a bounded Rust-backed subset one regex slice at a time; the published frontier now includes the broader `{1,4}` grouped-alternation slice with zero published correctness gaps, and the project remains far from drop-in `re` parity. |
| Delivery estimate | Foundation work is complete, benchmark reporting is live, and most published workloads now have real `rebar` timings; the newest `{1,4}` grouped-alternation slice is now behind the Rust boundary, but its Python-path benchmark catch-up is still missing. |
| Current milestone | Milestone 2 now has the broader `{1,4}` grouped-alternation slice behind the Rust boundary; the next planning pass should seed its Python-path benchmark catch-up so benchmark coverage stops lagging correctness. |
| Work queue | `0` ready, `0` in progress, `271` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `701` |
| Passing in published slice | `701` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `81` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, benchmark reporting is live, and most published workloads now have real `rebar` timings; the newest `{1,4}` grouped-alternation slice is now behind the Rust boundary, but its Python-path benchmark catch-up is still missing._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `456` |
| Workloads with real `rebar` timings | `424` |
| Known-gap workloads | `32` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `424` of `456` published workloads have real `rebar` timings._

### Immediate Next Steps

- Seed and land the Python-path benchmark catch-up for the broader `{1,4}` grouped-alternation slice so benchmark coverage catches up with the now-zero-gap correctness frontier.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Built-native benchmark results still live in separate sidecars with narrower coverage than the main published suite.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` is no longer just a harness scaffold. There is a real Rust core, a CPython-facing extension boundary, published correctness and benchmark reports, and a repeatable workflow for widening one bounded regex slice at a time.

The important caveat is still project shape, not raw counts: the published frontier is honest and coherent, but it remains small relative to stdlib `re`. Benchmarking is also still in the qualification phase. The main published suite measures the source-tree shim, while built-native runs are published separately so the repo can distinguish "measured" from "ready to claim faster than CPython."

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
