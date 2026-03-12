# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary, pattern-boundary, collection/replacement boundary, and literal-flag boundary benchmark packs plus the public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice plus observable compile-cache/purge behavior, local `escape()` parity, literal-only collection and replacement helpers, the first literal-only API-level `IGNORECASE` behavior slice implemented, the literal-flag correctness and benchmark packs published, exported-helper metadata parity cleanup landed, bounded parser diagnostic parity landed, the supported compile/match/escape slice moved behind the Rust boundary, bounded inline-flag, lookbehind, and character-class `IGNORECASE` compile parity landed, benchmark adapter/provenance hardening in place, and the remaining parser-acceptance, collection/replacement boundary migration, and post-parser module-workflow gaps queued. |
| Current milestone | Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness and benchmark packs, the landed literal-only API-level `IGNORECASE` slice plus its published correctness and benchmark follow-ons, the landed bounded inline-flag, lookbehind, and character-class `IGNORECASE` compile parity slices, the remaining Rust-boundary migration task needed to stop deepening Python semantics, the remaining bounded parser acceptance tasks needed to finish the currently published parser-matrix debt plus compile-benchmark catch-up, the queued module-workflow cleanup tasks for the remaining published replacement and flag-sensitive gaps, and then a built-native benchmark smoke follow-on so publication paths stay aligned with the verified native import path. |
| Work queue | `9` ready, `0` in progress, `45` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `15` |
| Passing comparisons | `15` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `1` |
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

- Land `RBR-0041` so the remaining published parser-matrix compile gaps are worked off as bounded Rust-backed parity tasks instead of another broad parser rewrite.
- After `RBR-0041`, land `RBR-0042` so the compile-path benchmark report starts measuring the newly supported parser cases instead of staying effectively scaffold-only.
- After `RBR-0042`, land `RBR-0042A` so the already-supported collection and replacement helpers also move behind the Rust boundary before more workflow breadth lands.
- After `RBR-0042A`, land `RBR-0043` through `RBR-0048` so the remaining published module-workflow `unimplemented` cases are worked off as bounded Rust-backed replacement and flag-sensitive follow-ons before broadening the corpus again.
- After `RBR-0048`, land `RBR-0049` so the benchmark surface publishes a bounded built-native smoke report instead of relying entirely on source-tree-shim timings.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The supported compile, parser-diagnostic, literal-match, cache, and `escape()` slice now lives behind `rebar._rebar`, but the currently supported collection and replacement helpers still live in `python/rebar/__init__.py`; until `RBR-0042A` lands, the project can still accrete some real workflow semantics on the Python side even though the long-term contract is a Rust-backed drop-in module.
- The correctness harness now covers 80 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, and literal-flag layers, with 9 honest `unimplemented` outcomes and 0 explicit failures visible; the remaining published debt is now concentrated in the possessive-quantifier and atomic-group parser-matrix compile cases plus the already-published module-workflow follow-ons queued behind the remaining collection/replacement boundary migration task.
- The benchmark harness now measures 45 published workloads across the compile-path, module-boundary, pattern-boundary, collection/replacement-boundary, literal-flag-boundary, and regression/stability packs with explicit adapter-mode provenance, and 30 workloads now have real `rebar` timings, but compile-path coverage remains scaffold-only and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has forty completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose gaps instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, supports a tiny literal-only `compile`/`search`/`match`/`fullmatch` path for `str` and `bytes`, honors API-level `IGNORECASE` for that bounded literal-only match slice, reuses supported `compile()` results through an observable cache, returns concrete `Pattern`/`Match` scaffolds for that subset, implements a local `escape()` helper with CPython-shaped `str`/`bytes` behavior, supports literal-only `split`/`findall`/`finditer` plus `sub`/`subn`, and publishes dedicated module-workflow, collection/replacement, and literal-flag correctness layers with no remaining explicit failures in the current scorecard. The compile, parser-diagnostic, literal-match, cache-visible metadata, API-level `IGNORECASE`, `escape()`, bounded inline-flag compile, bounded lookbehind compile, and bounded character-class `IGNORECASE` compile slice now crosses the Rust extension boundary; the remaining Python-owned semantics are concentrated in the supported collection and replacement helpers, which are queued for `RBR-0042A` before more workflow breadth lands. The benchmark layer now separates module-helper timings from precompiled `Pattern`, collection/replacement, and literal-flag boundary timings, but the compile-path suite is still scaffold-only and the main published report still runs through the source-tree shim. The near-term queue is now the remaining parser compile-parity catch-up (`RBR-0041`), compile benchmark catch-up, Rust-backed collection/replacement migration, the remaining replacement and flag-sensitive workflow follow-ons, and then a built-native benchmark smoke publication task.

## What The Numbers Mean

The correctness report is honest by construction: it records real passes, explicit failures, and explicit `unimplemented` outcomes separately. A larger published case count means the harness is seeing more of the surface area, not that the engine is close to complete.

The benchmark report is also still infrastructure-first. It has a useful workload inventory, provenance, gap accounting, and distinct precompiled-pattern, collection/replacement, and literal-flag boundary packs, but only `30` of `45` published workloads currently produce real `rebar` timings, and those measurements still run through the source-tree shim instead of the built native path. Until compile and match workloads are both implemented and measured, performance headlines stay out of the landing page.

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
