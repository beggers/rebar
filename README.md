# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary and pattern-boundary benchmark packs plus the public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice plus observable compile-cache/purge behavior and local `escape()` parity now implemented, benchmark adapter/provenance hardening in place, and the remaining helper/workflow/scorecard gaps queued. |
| Current milestone | Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, and the precompiled pattern-boundary benchmark pack by adding module-workflow correctness coverage, the first literal-only collection/replacement helpers, their follow-on correctness/benchmark packs, the next bounded literal-flag slice, and then targeted metadata-parity cleanup for the remaining exported-helper and compiled-pattern correctness failures. |
| Work queue | `9` ready, `0` in progress, `29` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `54` |
| Passing comparisons | `33` |
| Explicit failures | `8` |
| Honest gaps (`unimplemented`) | `13` |
| Covered manifests | `6` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `25` |
| Workloads with real `rebar` timings | `12` |
| Known-gap workloads | `13` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_README speedup rollups stay omitted while only `12` of `25` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0027` so the new literal-only match/cache/`escape()` slice is followed immediately by an end-to-end module-workflow correctness pack covering compile/search/match/fullmatch flows, cache/purge observations, and `escape()` parity.
- Keep `RBR-0028` through `RBR-0031` directly behind that workflow slice so the queue extends from literal-only collection and replacement helpers straight into their correctness and benchmark scorecards instead of stalling after implementation-only helper work.
- Roll from `RBR-0031` into `RBR-0032` through `RBR-0034` so the next bounded behavior slice tackles literal-only `IGNORECASE` parity and its scorecards before the roadmap jumps to broader parser or engine work.
- After `RBR-0034`, land `RBR-0035` and `RBR-0036` so the current exported-helper and compiled-pattern metadata mismatches are reduced as explicit correctness debt before the roadmap broadens again.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer, published match-behavior smoke coverage, CPython-shaped exported flags/constants, a concrete `Pattern` scaffold, real literal-only `Match` behavior, observable compile-cache/purge behavior, a local `escape()` helper, and measured precompiled-pattern helper timings, but module-workflow coverage, the broader collection/replacement/flag scorecards, and the remaining metadata-parity fixes are still outside the published compatibility surface.
- The correctness harness now covers 44 published cases across parser, module-API, match-behavior, exported-symbol, and pattern-object layers, but 13 `rebar` comparisons still end in honest `unimplemented` outcomes, 8 more still fail explicitly, and there is no module-workflow layer yet.
- The benchmark harness now measures 25 published workloads across the compile-path, module-boundary, pattern-boundary, and regression/stability packs with explicit adapter-mode provenance, and 12 workloads now have real `rebar` timings, but compile-path coverage remains scaffold-only and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has twenty-six completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose gaps instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, supports a tiny literal-only `compile`/`search`/`match`/`fullmatch` path for `str` and `bytes`, reuses supported `compile()` results through an observable cache, returns concrete `Pattern`/`Match` scaffolds for that bounded subset, and implements a local `escape()` helper with CPython-shaped `str`/`bytes` behavior. The benchmark layer now also separates module-helper timings from precompiled `Pattern` helper timings. Most collection, replacement, flag-sensitive, and general regex behavior is still explicitly unimplemented. The next queue slice is module-workflow correctness, then literal-only collection/replacement helpers, bounded literal-flag behavior, and cleanup for the remaining metadata-parity failures.

## What The Numbers Mean

The correctness report is honest by construction: it records real passes, explicit failures, and explicit `unimplemented` outcomes separately. A larger published case count means the harness is seeing more of the surface area, not that the engine is close to complete.

The benchmark report is also still infrastructure-first. It has a useful workload inventory, provenance, gap accounting, and now a distinct precompiled-pattern boundary pack, but only `12` of `25` published workloads currently produce real `rebar` timings, and those measurements still run through the source-tree shim instead of the built native path. Until compile and match workloads are both implemented and measured, performance headlines stay out of the landing page.

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
