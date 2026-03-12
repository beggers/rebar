# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary benchmark pack and public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice now implemented, benchmark adapter/provenance hardening in place, and the remaining cache/helper/reporting gaps queued. |
| Current milestone | Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds plus the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice by adding compile-cache/purge observability, `escape()` parity, precompiled-pattern and module-workflow scorecard coverage, the first literal-only collection/replacement helpers, and their follow-on correctness/benchmark packs on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exact CPython baseline metadata, the Phase 2 public-API correctness scorecard, the first Phase 3 match-behavior smoke pack, the regression/stability benchmark pack, benchmark adapter/provenance reporting, and the pattern-object correctness pack. |
| Work queue | `7` ready, `0` in progress, `26` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `44` |
| Passing comparisons | `22` |
| Explicit failures | `8` |
| Honest gaps (`unimplemented`) | `14` |
| Covered manifests | `5` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `19` |
| Workloads with real `rebar` timings | `2` |
| Known-gap workloads | `17` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_README speedup rollups stay omitted while only `2` of `19` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0024` and `RBR-0025` so the first literal-only behavior slice gains observable compile-cache/purge behavior and a real `escape()` helper instead of stopping at match-object scaffolding.
- Use `RBR-0026` and `RBR-0027` directly behind that cache/escape work so the published benchmark and correctness scorecards start reflecting precompiled-pattern overhead and end-to-end module workflows.
- Keep `RBR-0028` through `RBR-0031` directly behind the current cache/escape/reporting slice so the queue extends from literal-only collection and replacement helpers straight into their correctness and benchmark scorecards instead of stalling after implementation-only helper work.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer, published match-behavior smoke coverage, CPython-shaped exported flags/constants, a concrete `Pattern` scaffold, and real literal-only `Match` behavior, but cache/purge observability, `escape()` parity, and module-workflow coverage are still outside the published compatibility surface.
- The correctness harness now covers 44 published cases across parser, module-API, match-behavior, exported-symbol, and pattern-object layers, but 14 `rebar` comparisons still end in honest `unimplemented` outcomes, 8 more still fail explicitly, and there is no module-workflow layer yet.
- The benchmark harness now measures 19 published workloads across the compile-path, module-boundary, and regression/stability packs with explicit adapter-mode provenance, but only 2 workloads have real `rebar` timings so compile and match performance claims are still premature and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has twenty-three completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose gaps instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, supports a tiny literal-only `compile`/`search`/`match`/`fullmatch` path for `str` and `bytes`, and returns concrete `Pattern`/`Match` scaffolds for that bounded subset. Most collection, replacement, cache-observability, and general regex behavior is still explicitly unimplemented. The next queue slice is about cache visibility, `escape()` parity, module-workflow coverage, and then the first literal-only collection/replacement helpers.

## What The Numbers Mean

The correctness report is honest by construction: it records real passes, explicit failures, and explicit `unimplemented` outcomes separately. A larger published case count means the harness is seeing more of the surface area, not that the engine is close to complete.

The benchmark report is also still infrastructure-first. It has a useful workload inventory, provenance, and gap accounting, but only a small subset currently produces real `rebar` timings, and those measurements still run through the source-tree shim instead of the built native path. Until compile and match workloads are both implemented and measured, performance headlines stay out of the landing page.

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
