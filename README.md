# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is focused on expanding a still-bounded Rust-backed `re` subset while keeping the correctness and benchmark publications caught up with each newly supported slice. |
| Compatibility outlook | Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, simple alternation, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one bounded optional-group alternation slice, and bounded two-arm, omitted-no-arm, explicit-empty-else, plus empty-yes-arm conditional group-exists slices now pass through the Rust boundary; fully-empty conditional forms, broader ranged repeats, broader quantified alternation, and broader backtracking remain ahead of the frontier. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `11` ready, `0` in progress, `121` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `212` |
| Passing in published slice | `212` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `31` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall feature status: Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, simple alternation, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one bounded optional-group alternation slice, and bounded two-arm, omitted-no-arm, explicit-empty-else, plus empty-yes-arm conditional group-exists slices now pass through the Rust boundary; fully-empty conditional forms, broader ranged repeats, broader quantified alternation, and broader backtracking remain ahead of the frontier._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `219` |
| Workloads with real `rebar` timings | `169` |
| Known-gap workloads | `50` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `169` of `219` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0115` so the newly Rust-backed empty-yes-arm group-exists forms `(?(1)|else)` / `(?(name)|else)` also reach the published benchmark surface instead of remaining correctness-only coverage.
- After `RBR-0115`, land `RBR-0116` so the fully empty group-exists forms `(?(1)|)` / `(?(name)|)` are published before rejected-syntax diagnostics or broader backtracking reopen the frontier.
- After `RBR-0118`, land `RBR-0119` so assertion-conditioned conditional forms become an explicit rejected-syntax diagnostic slice instead of leaving the worker queue to stop at the last accepted empty-arm form.
- After `RBR-0120`, land `RBR-0121` so one wider `{1,3}` ranged-repeat quantified-group slice is published before quantified alternation or broader backtracking reopen the frontier.
- After `RBR-0123`, land `RBR-0124` so the queue reopens with one bounded `a(b|c){1,2}d` / `a(?P<word>b|c){1,2}d` quantified-alternation correctness slice instead of jumping straight to broader backtracking.

### Current Risks

- The repo now publishes `reports/benchmarks/native_smoke.json` from a real built `rebar._rebar` path and the benchmark harness can distinguish shim versus built-native execution modes, but the primary `reports/benchmarks/latest.json` report still measures the default source-tree shim rather than the dedicated built-native timing path, so routine full-suite measurement can still drift away from the verified install/import path.
- The supported compile, parser-diagnostic, literal-match, cache, `escape()`, collection/replacement helper, bounded replacement-template/callable replacement, bounded single-dot wildcard, inline-flag, bytes-`LOCALE`, grouped-literal replacement-template, grouped numbered-capture, grouped-segment parity, named-group metadata, bounded named-group replacement-template, bounded named-backreference, bounded numbered-backreference, bounded top-level literal-alternation, bounded grouped-alternation workflow slice, bounded grouped-alternation replacement-template workflow, bounded grouped-alternation callable-replacement workflow, bounded nested-group match workflow, bounded nested-group replacement-template workflow, bounded nested-group callable-replacement workflow, bounded nested-group alternation workflow, bounded branch-local backreference workflow, bounded optional-group quantifier workflow, bounded exact-repeat quantified-group workflow, one bounded ranged-repeat quantified-group workflow, one bounded optional-group alternation workflow, and bounded two-arm, omitted-no-arm, explicit-empty-else, plus empty-yes-arm conditional group-exists workflows now live behind `rebar._rebar`; fully-empty conditional forms, broader ranged repeats, broader quantified alternation, and broader backtracking are still ahead of the active Rust-backed frontier.
- The correctness harness now covers 212 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, literal-flag, grouped-match, named-group, named-group replacement, named-backreference, numbered-backreference, grouped-segment, literal-alternation, grouped-alternation, grouped-alternation replacement, grouped-alternation callable-replacement, nested-group, nested-group replacement, nested-group callable-replacement, nested-group alternation, branch-local backreference, optional-group, exact-repeat quantified-group, ranged-repeat quantified-group, optional-group alternation, conditional group-exists, conditional group-exists no-else, conditional group-exists empty-else, and conditional group-exists empty-yes-else layers, with 212 passes, 0 explicit failures, and 0 honest `unimplemented` outcomes; the active queued frontier is bounded empty-yes-arm benchmark catch-up in `RBR-0115`, bounded fully-empty conditional work in `RBR-0116` through `RBR-0118`, bounded assertion-conditioned diagnostic work in `RBR-0119` through `RBR-0120`, bounded wider ranged-repeat work in `RBR-0121` through `RBR-0123`, and bounded quantified alternation work in `RBR-0124` through `RBR-0126`.
- The benchmark harness now measures 208 published workloads across 25 manifests with explicit adapter-mode provenance, and 162 workloads now have real `rebar` timings; the remaining 46 known gaps are concentrated in the compile-matrix, module-boundary, grouped-named-boundary, numbered-backreference-boundary, grouped-alternation-boundary, grouped-alternation-replacement-boundary, grouped-alternation-callable-replacement-boundary, literal-flag-boundary, nested-group-boundary, nested-group-alternation-boundary, nested-group-replacement-boundary, nested-group-callable-replacement-boundary, branch-local-backreference-boundary, optional-group-boundary, exact-repeat-quantified-group-boundary, ranged-repeat-quantified-group-boundary, optional-group-alternation-boundary, conditional-group-exists-boundary, conditional-group-exists-no-else-boundary, conditional-group-exists-empty-else-boundary, and regression-matrix manifests, and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker continues to make forward progress under the hardened harness, but throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose the current supported frontier and the remaining unsupported surface instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now supports a real but still-bounded subset: literal compile/search/match/fullmatch, cache visibility, `escape()`, collection/replacement helpers, API-level `IGNORECASE`, grouped and named captures, bounded replacement-template and callable replacement workflows, bounded numbered and named backreferences, bounded grouped/nested alternation, bounded branch-local backreferences, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one bounded optional-group alternation slice, and bounded two-arm, omitted-no-arm, explicit-empty-else, plus empty-yes-arm conditional group-exists slices through both module and compiled-`Pattern` entrypoints. The published correctness surface is now `212` cases across `31` manifests with the current published slice at `212/212` passes and zero honest gaps. That still reflects only a bounded subset rather than overall stdlib `re` parity. The next queued frontier is empty-yes-arm conditional benchmark catch-up in `RBR-0115`, followed by fully-empty conditional publication/parity/benchmark work in `RBR-0116` through `RBR-0118`, bounded assertion-conditioned diagnostic publication/parity in `RBR-0119` through `RBR-0120`, one wider ranged-repeat publication/parity/benchmark slice in `RBR-0121` through `RBR-0123`, and one bounded quantified-alternation publication/parity/benchmark slice in `RBR-0124` through `RBR-0126`.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is honest by construction: `212` passes out of `212` published cases means the currently published slice has no hidden gaps, not that `rebar` is anywhere near full stdlib `re` parity. Fully-empty conditional forms, broader quantified alternation, broader ranged repeats, and broader backtracking still remain ahead of the frontier.

The benchmark report is also a coverage report before it is a performance story. The status block above carries the current measured-versus-gap totals, and the main `reports/benchmarks/latest.json` run still exercises the source-tree shim rather than the full built-native path. Until compile and match workloads are both implemented and measured through the main publication path, performance headlines stay out of the landing page.

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
