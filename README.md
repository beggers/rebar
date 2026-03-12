# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is focused on expanding a still-bounded Rust-backed `re` subset while keeping the correctness and benchmark publications caught up with each newly supported slice. |
| Compatibility outlook | Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, and simple alternation now pass through the Rust boundary, but quantified groups, conditionals, and broader backtracking remain ahead of the frontier. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `13` ready, `0` in progress, `96` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `164` |
| Passing in published slice | `164` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `23` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall feature status: Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, and simple alternation now pass through the Rust boundary, but quantified groups, conditionals, and broader backtracking remain ahead of the frontier._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `139` |
| Workloads with real `rebar` timings | `113` |
| Known-gap workloads | `26` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `113` of `139` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0090` so the bounded branch-local backreference cases published by `RBR-0089` become real Rust-backed behavior before quantified branches or broader backtracking reopen the frontier.
- After `RBR-0090`, land `RBR-0091` so branch-local backreference behavior reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0091`, land `RBR-0092` and `RBR-0093` so the queue reopens quantified execution through one bounded optional-group slice before counted repeats, quantified alternation, conditionals, or broader backtracking reopen the frontier.
- After `RBR-0093`, land `RBR-0094` so the first optional-group quantifier slice reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0094`, land `RBR-0095` and `RBR-0096` so quantified execution continues through one bounded exact-repeat quantified-group slice before ranged repeats, quantified alternation, conditionals, or broader backtracking reopen the frontier.
- After `RBR-0096`, land `RBR-0097` so the first deterministic counted-repeat slice reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0097`, land `RBR-0098` and `RBR-0099` so quantified execution broadens from exact counts into one bounded ranged-repeat slice before quantified alternation, conditionals, or broader backtracking reopen the frontier.
- After `RBR-0099`, land `RBR-0100` so the first bounded counted-range slice reaches the published benchmark surface promptly instead of becoming another correctness-only island.
- After `RBR-0100`, land `RBR-0101` and `RBR-0102` so the queue combines already-supported optional quantifiers and grouped alternation before conditionals or broader backtracking reopen the frontier.
- After `RBR-0102`, land `RBR-0103` so the first bounded optional-group alternation slice reaches the published benchmark surface promptly instead of becoming another correctness-only island.

### Current Risks

- The repo now publishes `reports/benchmarks/native_smoke.json` from a real built `rebar._rebar` path and the benchmark harness can distinguish shim versus built-native execution modes, but the primary `reports/benchmarks/latest.json` report still measures the default source-tree shim rather than the dedicated built-native timing path, so routine full-suite measurement can still drift away from the verified install/import path.
- The supported compile, parser-diagnostic, literal-match, cache, `escape()`, collection/replacement helper, bounded replacement-template/callable replacement, bounded single-dot wildcard, inline-flag, bytes-`LOCALE`, grouped-literal replacement-template, grouped numbered-capture, grouped-segment parity, named-group metadata, bounded named-group replacement-template, bounded named-backreference, bounded numbered-backreference, bounded top-level literal-alternation, bounded grouped-alternation workflow slice, bounded grouped-alternation replacement-template workflow, bounded grouped-alternation callable-replacement workflow, bounded nested-group match workflow, bounded nested-group replacement-template workflow, bounded nested-group callable-replacement workflow, and bounded nested-group alternation workflow now live behind `rebar._rebar`; the next execution queue is branch-local backreference parity/benchmark catch-up, optional-group quantifier publication, exact-repeat quantified-group publication, ranged-repeat quantified-group publication, and optional-group alternation publication rather than debt inside the existing twenty-three-manifest correctness surface.
- The correctness harness now covers 164 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, literal-flag, grouped-match, named-group, named-group replacement, named-backreference, numbered-backreference, grouped-segment, literal-alternation, grouped-alternation, grouped-alternation replacement, grouped-alternation callable-replacement, nested-group, nested-group replacement, nested-group callable-replacement, nested-group alternation, and branch-local backreference layers, with 158 passes, 0 explicit failures, and 6 honest `unimplemented` outcomes; the active queued frontier is bounded branch-local backreference parity in `RBR-0090` before optional-group quantifier, exact-repeat quantified-group, ranged-repeat quantified-group, and optional-group alternation follow-ons.
- The benchmark harness now measures 139 published workloads across the compile-path, module-boundary, pattern-boundary, collection/replacement-boundary, literal-flag-boundary, regression/stability, grouped-named, numbered-backreference, grouped-alternation, grouped-alternation replacement, grouped-alternation callable-replacement, nested-group, nested-group alternation, nested-group replacement, and nested-group callable-replacement boundary packs with explicit adapter-mode provenance, and 113 workloads now have real `rebar` timings; the remaining 26 known gaps are concentrated in the compile-matrix, module-boundary, grouped-named-boundary, numbered-backreference-boundary, grouped-alternation-boundary, grouped-alternation-replacement-boundary, grouped-alternation-callable-replacement-boundary, literal-flag-boundary, nested-group-boundary, nested-group-alternation-boundary, nested-group-replacement-boundary, nested-group-callable-replacement-boundary, and regression-matrix manifests, and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has ninety completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose the current supported frontier and the remaining unsupported surface instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now supports a real but still-bounded subset: literal compile/search/match/fullmatch, cache visibility, `escape()`, collection/replacement helpers, API-level `IGNORECASE`, grouped and named captures, bounded replacement-template and callable replacement workflows, bounded numbered and named backreferences, and bounded grouped/nested alternation through both module and compiled-`Pattern` entrypoints. The published correctness scorecard now covers `164` cases across `23` manifests, with `158` passing comparisons and `6` honest `unimplemented` branch-local backreference gaps; that reflects the current implemented slice plus one newly published frontier, not overall stdlib `re` parity. The next queued frontier is branch-local backreference parity, then the first quantified-group slices.

Benchmark publication is still partial by design. `reports/benchmarks/latest.json` now covers `139` workloads with `113` real `rebar` timings and `26` explicit known gaps, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is honest by construction: `158` passing comparisons out of `164` published cases means the currently implemented slice matches CPython where `rebar` claims support, while the remaining `6` published cases stay visible as explicit branch-local backreference gaps. `rebar` is still early and bounded overall; quantified groups, conditionals, and broader backtracking remain ahead of the frontier.

The benchmark report is also a coverage report before it is a performance story. It currently publishes `139` workloads with `113` measured `rebar` timings and `26` explicit gaps, and the main `reports/benchmarks/latest.json` run still exercises the source-tree shim rather than the full built-native path. Until compile and match workloads are both implemented and measured through the main publication path, performance headlines stay out of the landing page.

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
