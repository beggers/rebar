# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary, pattern-boundary, collection/replacement boundary, and literal-flag boundary benchmark packs plus the public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice plus observable compile-cache/purge behavior, local `escape()` parity, literal-only collection and replacement helpers, the first literal-only API-level `IGNORECASE` behavior slice implemented, the literal-flag correctness and benchmark packs published, exported-helper metadata parity cleanup landed, bounded parser diagnostic parity landed, the supported compile/match/escape slice moved behind the Rust boundary, bounded inline-flag, lookbehind, character-class `IGNORECASE`, possessive-quantifier, and atomic-group compile parity landed, benchmark adapter/provenance hardening plus compile-benchmark catch-up landed, the supported collection/replacement workflow slice moved behind the Rust boundary, the bounded single-dot wildcard workflow slice plus inline-flag and bytes-`LOCALE` workflow parity landed, the grouped-literal replacement-template follow-on closed the last published correctness gap, the post-parser module-workflow benchmark catch-up landed, the dedicated built-native benchmark smoke report landed, the first grouped-match/capture correctness pack published, bounded grouped numbered-capture parity landed, the first named-group correctness pack published, bounded named-group parity landed, the first named-group replacement-template correctness pack published, bounded named-group replacement-template parity landed, the first named-backreference correctness pack published, bounded named-backreference parity landed, the grouped/named benchmark catch-up landed, the first numbered-backreference correctness pack published, bounded numbered-backreference parity landed, the numbered-backreference benchmark catch-up landed, the grouped-segment correctness pack published, bounded grouped-segment parity landed, the grouped-segment benchmark catch-up landed, the literal-alternation correctness pack published, bounded literal-alternation parity landed, and literal-alternation benchmark catch-up, grouped-alternation, grouped-alternation replacement, and grouped-alternation callable-replacement work are queued. |
| Current milestone | Milestone 2: build on the landed exported-symbol and compiled-pattern scaffolds, the first literal-only `compile`/`search`/`match`/`fullmatch` behavior slice, observable compile-cache/purge behavior, local `escape()` parity, the module-workflow correctness pack, the precompiled pattern-boundary benchmark pack, the first literal-only collection and replacement helpers, their published correctness and benchmark packs, the landed literal-only API-level `IGNORECASE` slice plus its published correctness and benchmark follow-ons, the landed bounded inline-flag, lookbehind, character-class `IGNORECASE`, possessive-quantifier, and atomic-group compile parity slices, the landed compile-benchmark catch-up that now measures the supported parser cases honestly, the landed Rust-backed collection/replacement boundary, the landed single-dot wildcard workflow slice plus inline-flag, bytes-`LOCALE`, and grouped-literal replacement-template workflow parity, the landed post-parser module-workflow benchmark catch-up, the landed built-native benchmark smoke report, the first grouped-match/capture correctness pack, the landed grouped numbered-capture parity slice, the landed named-group correctness pack, the landed bounded named-group parity slice, the first named-group replacement-template correctness pack, the landed bounded named-group replacement-template parity slice, the first named-backreference correctness pack, the landed bounded named-backreference parity slice, the landed grouped/named benchmark catch-up, the first numbered-backreference correctness pack, the landed bounded numbered-backreference parity slice, the landed numbered-backreference benchmark catch-up, the grouped-segment correctness pack published, the landed grouped-segment parity slice, the landed grouped-segment benchmark catch-up, the literal-alternation correctness pack published, the landed literal-alternation parity slice, and now literal-alternation benchmark catch-up, grouped-alternation, grouped-alternation replacement, and grouped-alternation callable-replacement follow-ons so the queue stays ahead of the current publication frontier. |
| Work queue | `9` ready, `0` in progress, `72` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `108` |
| Passing comparisons | `108` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `15` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `76` |
| Workloads with real `rebar` timings | `59` |
| Known-gap workloads | `17` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_README speedup rollups stay omitted while only `59` of `76` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0067` so the benchmark report catches the new literal-alternation slice up before grouped alternation reopens the correctness frontier.
- After `RBR-0067`, land `RBR-0068` and `RBR-0069` so the queue combines already-supported grouping and alternation before broader backtracking or quantifier work reopens the frontier.
- After `RBR-0069`, land `RBR-0070` so grouped-alternation behavior reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0070`, land `RBR-0071` and `RBR-0072` so the queue combines already-supported grouped alternation and replacement-template behavior before nested groups or quantified branches reopen the frontier.
- After `RBR-0072`, land `RBR-0073` so grouped-alternation replacement behavior reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0073`, land `RBR-0074` and `RBR-0075` so the queue extends into grouped-alternation callable replacement before nested groups or quantified branches reopen the frontier.
- After `RBR-0075`, land `RBR-0076` so grouped-alternation callable-replacement behavior reaches the published benchmark surface promptly instead of becoming another correctness-only island.

### Current Risks

- The repo now publishes `reports/benchmarks/native_smoke.json` from a real built `rebar._rebar` path and the benchmark harness can distinguish shim versus built-native execution modes, but the primary `reports/benchmarks/latest.json` report still measures the default source-tree shim rather than the dedicated built-native timing path, so routine full-suite measurement can still drift away from the verified install/import path.
- The supported compile, parser-diagnostic, literal-match, cache, `escape()`, collection/replacement helper, bounded replacement-template/callable replacement, bounded single-dot wildcard, inline-flag, bytes-`LOCALE`, grouped-literal replacement-template, grouped numbered-capture, grouped-segment parity, named-group metadata, bounded named-group replacement-template, bounded named-backreference, bounded numbered-backreference, and bounded top-level literal-alternation workflow slice now lives behind `rebar._rebar`, and the next execution frontier is literal-alternation benchmark catch-up, grouped alternation, grouped-alternation replacement, and grouped-alternation callable replacement rather than debt inside the existing fifteen-manifest surface.
- The correctness harness now covers 108 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, literal-flag, grouped-match, named-group, named-group replacement, named-backreference, numbered-backreference, grouped-segment, and literal-alternation layers, with 108 passes, 0 explicit failures, and 0 honest `unimplemented` outcomes; the next queued correctness frontier is grouped alternation publication in `RBR-0068`, with literal-alternation benchmark catch-up queued first in `RBR-0067`.
- The benchmark harness now measures 71 published workloads across the compile-path, module-boundary, pattern-boundary, collection/replacement-boundary, literal-flag-boundary, regression/stability, grouped-named, numbered-backreference, and grouped-segment packs with explicit adapter-mode provenance, and 56 workloads now have real `rebar` timings; the remaining 15 known gaps are concentrated in the compile-matrix, module-boundary, literal-flag-boundary, regression-matrix, grouped-named-boundary, numbered-backreference-boundary, and grouped-segment-boundary manifests, and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has sixty-seven completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose the current supported frontier and the remaining unsupported surface instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, supports a tiny literal-only `compile`/`search`/`match`/`fullmatch` path for `str` and `bytes`, honors API-level `IGNORECASE` for that bounded literal-only match slice, reuses supported `compile()` results through an observable cache, returns concrete `Pattern`/`Match` scaffolds for that subset, implements a local `escape()` helper with CPython-shaped `str`/`bytes` behavior, supports literal-only `split`/`findall`/`finditer` plus `sub`/`subn`, including bounded whole-match replacement-template and callable replacement variants for supported literal `str` workflows, and supports bounded grouped-literal numbered-capture, grouped-segment, named-group metadata/runtime behavior, bounded named-group replacement-template behavior, bounded named-backreference behavior, bounded numbered-backreference behavior, and bounded top-level literal alternation through both module and compiled-`Pattern` flows. The published correctness scorecard now sits at 108 cases across 15 manifests, with 108 passes, 0 explicit failures, and 0 honest `unimplemented` outcomes after landing the bounded top-level literal-alternation slice. The compile, parser-diagnostic, literal-match, cache-visible metadata, API-level `IGNORECASE`, `escape()`, supported collection/replacement helper, bounded replacement-template/callable replacement, bounded single-dot wildcard, inline-flag, bytes-`LOCALE`, grouped-literal replacement-template, grouped numbered-capture, grouped-segment parity, named-group metadata, bounded named-group replacement-template, bounded named-backreference, bounded numbered-backreference, and bounded top-level literal-alternation slice now cross the Rust extension boundary. The benchmark layer now separates module-helper timings from precompiled `Pattern`, collection/replacement, and literal-flag boundary timings, the compile-path suite records five real `rebar` compile timings plus one honest gap instead of staying scaffold-only, the grouped-segment benchmark catch-up has now landed, the combined source-tree benchmark report now covers 71 workloads with 56 real `rebar` timings and 15 explicit gaps, and a dedicated `reports/benchmarks/native_smoke.json` artifact still measures a separate six-workload smoke slice through a real built-native `rebar._rebar` path. The near-term queue is now literal-alternation benchmark catch-up, grouped alternation, grouped-alternation replacement, and grouped-alternation callable replacement behind that branch-selection frontier.

## What The Numbers Mean

The correctness report is honest by construction: it records real passes, explicit failures, and explicit `unimplemented` outcomes separately. A larger published case count means the harness is seeing more of the surface area, not that the engine is close to complete.

The benchmark report is also still infrastructure-first. It has a useful workload inventory, provenance, gap accounting, and distinct compile-path, precompiled-pattern, collection/replacement, literal-flag, regression, grouped/named, numbered-backreference, and grouped-segment boundary packs, but only `56` of `71` published workloads currently produce real `rebar` timings, and the main `reports/benchmarks/latest.json` publication still runs through the source-tree shim instead of the built native path. A separate `reports/benchmarks/native_smoke.json` artifact now proves the built-native path for a six-workload smoke slice without claiming full-suite native publication. Until compile and match workloads are both implemented and measured through the main publication path, performance headlines stay out of the landing page.

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
| `reports/benchmarks/latest.json` | Latest published full benchmark scorecard, currently through the source-tree shim. |
| `reports/benchmarks/native_smoke.json` | Dedicated built-native smoke benchmark artifact for the verified `rebar._rebar` path. |
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
