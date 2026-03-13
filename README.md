# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is widening a real Rust-backed subset one bounded regex slice at a time, and the project is still far from drop-in `re` parity. |
| Delivery estimate | Foundation work is complete, but the published Rust-backed slice is still narrow and benchmark coverage is catching up immediately behind each newly landed parity slice. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `2` ready, `0` in progress, `263` done, `0` blocked |
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

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation work is complete, but the published Rust-backed slice is still narrow and benchmark coverage is catching up immediately behind each newly landed parity slice._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `447` |
| Workloads with real `rebar` timings | `413` |
| Known-gap workloads | `34` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `413` of `447` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0261` so the broader-range open-ended `{2,}` grouped-backtracking slice reaches published benchmark coverage after parity landed.
- Keep `RBR-0262` immediately behind that frontier so source-tree benchmark wrapper coverage can be consolidated as soon as the current grouped `{2,}` slice is fully caught up.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- Built-native benchmark results still live in separate sidecars with narrower workload coverage than the main published suite.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` is past the pure-harness stage. The repo now has a Rust core, a CPython-facing extension boundary, canonical correctness and benchmark publications, and a specialist-agent loop that keeps widening one bounded regex slice at a time.

The implementation frontier is real but still narrow. The published correctness slice is currently clean at 677 passing cases across 79 manifests, but that slice is still much smaller than the full stdlib `re` surface; the immediate queue is the broader-range open-ended grouped-backtracking `{2,}` benchmark catch-up, with benchmark-wrapper consolidation held directly behind it. Benchmarking is still coverage-first: the main report remains source-tree-shim based, while built-native full-suite and smoke runs live in separate sidecars so performance claims stay explicitly qualified.

## What The Numbers Mean

The counts in the status block are progress signals, not a claim of general drop-in parity. A clean published correctness slice means the currently documented frontier is internally consistent; it does not mean most accepted `re` syntax or behavior is implemented yet.

The benchmark totals are coverage signals too. The main suite still has known gaps and still measures the source-tree shim, so broad speed claims stay out of the README; the built-native sidecars exist to keep that distinction visible until benchmark publication is unified.

## Operating Model

The repo now runs with a specialist-agent loop. The supervisor only tunes the harness and agent set; architecture and feature-planning agents seed concrete work; the Feature Implementation Agent executes the ready queue; the QA+testing agent widens or hardens test coverage; the implementation-faithfulness agent repairs implementation-only test failures; the cleanup agent removes duplication and unnecessary code without changing overall behavior; and the reporting agent keeps the landing page honest. Durable context lives under `ops/state/`; ephemeral execution traces live under `.rebar/runtime/`.

## Important Paths

| Path | Purpose |
| --- | --- |
| `ops/state/current_status.md` | Durable project status, risks, and near-term next steps. |
| `ops/state/backlog.md` | Ordered milestone queue plus supervisor notes about sequencing. |
| `ops/tasks/` | Ready, in-progress, done, and blocked task queues. |
| `ops/user_asks/inbox/` | Supervisor-owned intake for future human notes and harness requests. |
| `.rebar/runtime/dashboard.md` | Latest cycle health, git state, and queue counts. |
| `reports/correctness/latest.json` | Latest published correctness scorecard. |
| `reports/benchmarks/latest.json` | Latest published full benchmark scorecard, currently through the source-tree shim. |
| `reports/benchmarks/native_full.json` | Strict built-native sidecar for the full published benchmark suite. |
| `reports/benchmarks/native_smoke.json` | Dedicated built-native smoke benchmark artifact for the verified `rebar._rebar` path. |
| `python/rebar/__init__.py` | Current Python-facing shim and scaffold behavior. |
| `python/rebar_harness/` | Correctness and benchmark runners. |

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
- The supervisor is expected to tune the harness and agent set, while the specialist workers own queue shaping, README quality, test growth, and implementation work inside their scoped roles.
