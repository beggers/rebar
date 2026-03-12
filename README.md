# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary, pattern-boundary, and collection/replacement boundary benchmark packs plus the public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice plus observable compile-cache/purge behavior, local `escape()` parity, literal-only collection and replacement helpers, the first literal-only API-level `IGNORECASE` behavior slice implemented, the literal-flag correctness pack published, benchmark adapter/provenance hardening in place, and the remaining literal-flag benchmark, metadata, and parser-diagnostic gaps queued. |
| Current milestone | Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness pack, the matching collection/replacement benchmark pack, the landed literal-only API-level `IGNORECASE` slice plus its published correctness follow-on, the queued literal-flag benchmark follow-on, targeted metadata-parity cleanup for the remaining exported-helper and compiled-pattern correctness failures, and finally the bounded parser diagnostic/acceptance tasks needed to finish the currently published parser-matrix debt plus compile-benchmark catch-up. |
| Work queue | `8` ready, `0` in progress, `36` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `80` |
| Passing comparisons | `52` |
| Explicit failures | `8` |
| Honest gaps (`unimplemented`) | `20` |
| Covered manifests | `8` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `45` |
| Workloads with real `rebar` timings | `30` |
| Known-gap workloads | `15` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_README speedup rollups stay omitted while only `30` of `45` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0034` so the newly published literal-only `IGNORECASE` correctness slice also reaches the benchmark scorecard before the roadmap jumps to broader parser or engine work.
- After `RBR-0034`, land `RBR-0035` and `RBR-0036` so the current exported-helper and compiled-pattern metadata mismatches are reduced as explicit correctness debt before the roadmap broadens again.
- After `RBR-0036`, land `RBR-0037` through `RBR-0041` so the remaining published parser-matrix gaps are worked off as bounded diagnostic and compile-acceptance tasks instead of another broad parser rewrite.
- After `RBR-0041`, land `RBR-0042` so the compile-path benchmark report starts measuring the newly supported parser cases instead of staying effectively scaffold-only.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer, published match-behavior smoke coverage, CPython-shaped exported flags/constants, a concrete `Pattern` scaffold, real literal-only `Match` behavior, observable compile-cache/purge behavior, a local `escape()` helper, literal-only API-level `IGNORECASE` matching for representative `str` and `bytes` cases, literal-only `split`/`findall`/`finditer`/`sub`/`subn` behavior, published module-workflow, collection/replacement, and literal-flag correctness scorecards, and measured precompiled-pattern plus collection/replacement helper timings, but the literal-flag benchmark follow-on and the remaining metadata-parity fixes are still outside the published compatibility surface.
- The correctness harness now covers 80 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, and literal-flag layers, with 20 honest `unimplemented` outcomes and 8 explicit failures still visible; after the queued metadata and parser tasks land, the remaining visible debt is expected to concentrate in the published parser-matrix compile cases already queued as bounded follow-ons.
- The benchmark harness now measures 35 published workloads across the compile-path, module-boundary, pattern-boundary, collection/replacement-boundary, and regression/stability packs with explicit adapter-mode provenance, and 22 workloads now have real `rebar` timings, but compile-path coverage remains scaffold-only and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has thirty-three completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose gaps instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, supports a tiny literal-only `compile`/`search`/`match`/`fullmatch` path for `str` and `bytes`, honors API-level `IGNORECASE` for that bounded literal-only match slice, reuses supported `compile()` results through an observable cache, returns concrete `Pattern`/`Match` scaffolds for that subset, implements a local `escape()` helper with CPython-shaped `str`/`bytes` behavior, supports literal-only `split`/`findall`/`finditer` plus `sub`/`subn`, and publishes dedicated module-workflow, collection/replacement, and literal-flag correctness layers. The benchmark layer now separates module-helper timings from both precompiled `Pattern` helper timings and collection/replacement helper timings. The literal-flag benchmark follow-on, metadata-parity cleanup, and broader parser/engine coverage are still explicitly incomplete. The next queue slice is the bounded literal-flag benchmark pack, then metadata-parity cleanup for the remaining explicit failures, and then the seeded parser compile-parity tasks for the currently published parser-matrix gaps.

## What The Numbers Mean

The correctness report is honest by construction: it records real passes, explicit failures, and explicit `unimplemented` outcomes separately. A larger published case count means the harness is seeing more of the surface area, not that the engine is close to complete.

The benchmark report is also still infrastructure-first. It has a useful workload inventory, provenance, gap accounting, and distinct precompiled-pattern plus collection/replacement boundary packs, but only `22` of `35` published workloads currently produce real `rebar` timings, and those measurements still run through the source-tree shim instead of the built native path. Until compile and match workloads are both implemented and measured, performance headlines stay out of the landing page.

## Operating Model

The repo runs with a supervisor/implementation split. The supervisor maintains the harness, queue, state files, and README/reporting surfaces. The implementation worker takes one bounded task at a time and moves it to `done/` or `blocked/`. Durable context lives under `ops/state/`; ephemeral execution traces live under `.rebar/runtime/`.

## Important Paths

| Path | Purpose |
| --- | --- |
| `ops/state/current_status.md` | Durable project status, risks, and near-term next steps. |
| `ops/state/backlog.md` | Ordered milestone queue plus supervisor notes about sequencing. |
| `ops/tasks/` | Ready, in-progress, done, and blocked task queues. |
| `.rebar/runtime/dashboard.md` | Latest cycle health, git state, and queue counts. |
| `reports/correctness/latest.json` | Latest published correctness scorecard. |
| `reports/benchmarks/latest.json` | Latest published benchmark scorecard. |
| `python/rebar/__init__.py` | Current Python-facing shim and scaffold behavior. |
| `python/rebar_harness/` | Correctness and benchmark runners. |

## Useful Commands

```bash
python3 scripts/rebar_ops.py status
python3 scripts/rebar_ops.py report
python3 scripts/rebar_ops.py render supervisor
python3 scripts/rebar_ops.py cycle --force-agent implementation
python3 scripts/rebar_ops.py cycle --force-supervisor
bash scripts/loop_forever.sh
```

## Operating Notes

- Run the forever loop from a normal shell on a writable checkout.
- Do not start a second `python3 scripts/rebar_ops.py cycle ...` run against the same checkout while `scripts/loop_forever.sh` is active.
- Avoid launching the loop from inside another sandboxed Codex session; nested sandboxes can distort child-agent behavior and cache writes.
- The supervisor is expected to change the harness, reporting, and queue when that is the pragmatic way to keep the project moving.
