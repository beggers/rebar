# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is focused on expanding a still-bounded Rust-backed `re` subset while keeping the correctness and benchmark publications caught up with each newly supported slice. |
| Compatibility outlook | Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, simple alternation, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one wider bounded ranged-repeat quantified-group slice, one bounded quantified-alternation slice, one bounded optional-group alternation slice, bounded two-arm, omitted-no-arm, explicit-empty-else, empty-yes-arm, plus fully-empty conditional group-exists slices, and one bounded alternation-heavy explicit-empty-else conditional slice now pass through the Rust boundary; broader ranged repeats, broader quantified alternation, accepted conditional-replacement follow-ons, and broader backtracking-heavy conditional/grouped execution remain ahead of the frontier. |
| Current milestone | Milestone 2 keeps widening a narrow but real Rust-backed compatibility frontier, with correctness publication, Rust-backed parity, and benchmark catch-up landing in lockstep for each bounded regex slice. |
| Work queue | `15` ready, `0` in progress, `135` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `240` |
| Passing in published slice | `240` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `36` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall feature status: Early subset, not near drop-in feature parity yet: literals, captures, bounded replacement/backreference workflows, simple alternation, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one wider bounded ranged-repeat quantified-group slice, one bounded quantified-alternation slice, one bounded optional-group alternation slice, bounded two-arm, omitted-no-arm, explicit-empty-else, empty-yes-arm, plus fully-empty conditional group-exists slices, and one bounded alternation-heavy explicit-empty-else conditional slice now pass through the Rust boundary; broader ranged repeats, broader quantified alternation, accepted conditional-replacement follow-ons, and broader backtracking-heavy conditional/grouped execution remain ahead of the frontier._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `255` |
| Workloads with real `rebar` timings | `193` |
| Known-gap workloads | `62` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; built-native timing remains limited to [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json)._

_README speedup rollups stay omitted while only `193` of `255` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0129` so the newly supported bounded alternation-heavy explicit-empty-else conditional slice, pinned to `a(b)?c(?(1)(de|df)|)` / `a(?P<word>b)?c(?(word)(de|df)|)`, reaches the published benchmark surface before replacement-conditioned work or broader backtracking reopen the frontier.
- After `RBR-0129`, land `RBR-0130` so the queue reopens with a bounded omitted-no-arm conditional replacement slice, pinned to `a(b)?c(?(1)d)` / `a(?P<word>b)?c(?(word)d)` through `sub()` and `subn()`, before nested or quantified conditional composition reopens the frontier.
- After `RBR-0132`, land `RBR-0133` so the queue keeps the conditional-replacement frontier concrete with a bounded explicit-empty-else `a(b)?c(?(1)d|)` / `a(?P<word>b)?c(?(word)d|)` `sub()` and `subn()` slice before empty-yes-arm replacement, nested conditionals, or quantified conditionals reopen the frontier.
- After `RBR-0135`, land `RBR-0136` so the queue reopens with a bounded empty-yes-arm conditional replacement slice, pinned to `a(b)?c(?(1)|e)` / `a(?P<word>b)?c(?(word)|e)` through `sub()` and `subn()`, before fully-empty replacement, nested conditionals, quantified conditionals, or broader backtracking reopen the frontier.
- After `RBR-0138`, land `RBR-0139` so the queue keeps accepted conditional replacement work concrete with a bounded fully-empty `a(b)?c(?(1)|)` / `a(?P<word>b)?c(?(word)|)` `sub()` and `subn()` slice before nested conditionals, quantified conditionals, or broader backtracking reopen the frontier.

### Current Risks

- The repo now publishes `reports/benchmarks/native_smoke.json` from a real built `rebar._rebar` path and the benchmark harness can distinguish shim versus built-native execution modes, but the primary `reports/benchmarks/latest.json` report still measures the default source-tree shim rather than the dedicated built-native timing path, so routine full-suite measurement can still drift away from the verified install/import path.
- The supported compile, parser-diagnostic, literal-match, cache, `escape()`, collection/replacement helper, bounded replacement-template/callable replacement, bounded single-dot wildcard, inline-flag, bytes-`LOCALE`, grouped-literal replacement-template, grouped numbered-capture, grouped-segment parity, named-group metadata, bounded named-group replacement-template, bounded named-backreference, bounded numbered-backreference, bounded top-level literal-alternation, bounded grouped-alternation workflow slice, bounded grouped-alternation replacement-template workflow, bounded grouped-alternation callable-replacement workflow, bounded nested-group match workflow, bounded nested-group replacement-template workflow, bounded nested-group callable-replacement workflow, bounded nested-group alternation workflow, bounded branch-local backreference workflow, bounded optional-group quantifier workflow, bounded exact-repeat quantified-group workflow, one bounded ranged-repeat quantified-group workflow, one wider bounded ranged-repeat quantified-group workflow, one bounded quantified-alternation workflow slice, one bounded optional-group alternation workflow, bounded two-arm, omitted-no-arm, explicit-empty-else, empty-yes-arm, plus fully-empty conditional group-exists workflows, and one bounded alternation-heavy explicit-empty-else conditional workflow now live behind `rebar._rebar`; broader ranged repeats, broader quantified alternation, accepted conditional-replacement follow-ons, and broader backtracking-heavy conditional/grouped execution are still ahead of the active Rust-backed frontier.
- The correctness harness now covers 240 published cases across parser, module-API, match-behavior, exported-symbol, pattern-object, module-workflow, collection/replacement, literal-flag, grouped-match, named-group, named-group replacement, named-backreference, numbered-backreference, grouped-segment, literal-alternation, grouped-alternation, grouped-alternation replacement, grouped-alternation callable-replacement, nested-group, nested-group replacement, nested-group callable-replacement, nested-group alternation, branch-local backreference, optional-group, exact-repeat quantified-group, ranged-repeat quantified-group, wider-ranged-repeat quantified-group, quantified alternation, optional-group alternation, conditional group-exists, conditional group-exists no-else, conditional group-exists empty-else, conditional group-exists empty-yes-else, conditional group-exists fully-empty, conditional group-exists assertion-diagnostics, and conditional group-exists empty-else alternation layers, with 240 passes, 0 explicit failures, and 0 honest `unimplemented` outcomes; the active queued frontier is bounded alternation-heavy explicit-empty-else conditional benchmark catch-up in `RBR-0129`, bounded omitted-no-arm, explicit-empty-else, empty-yes-arm, and fully-empty conditional replacement slices in `RBR-0130` through `RBR-0141`, and one bounded omitted-no-arm alternation-heavy conditional slice in `RBR-0142` through `RBR-0144`.
- The benchmark harness now measures 252 published workloads across 29 manifests with explicit adapter-mode provenance, and 189 workloads now have real `rebar` timings; the remaining 63 known gaps are concentrated in the compile-matrix, module-boundary, grouped-named-boundary, numbered-backreference-boundary, grouped-alternation-boundary, grouped-alternation-replacement-boundary, grouped-alternation-callable-replacement-boundary, literal-flag-boundary, nested-group-boundary, nested-group-alternation-boundary, nested-group-replacement-boundary, nested-group-callable-replacement-boundary, branch-local-backreference-boundary, optional-group-boundary, exact-repeat-quantified-group-boundary, ranged-repeat-quantified-group-boundary, wider-ranged-repeat-quantified-group-boundary, quantified-alternation-boundary, optional-group-alternation-boundary, conditional-group-exists-boundary, conditional-group-exists-no-else-boundary, conditional-group-exists-empty-else-boundary, conditional-group-exists-empty-yes-else-boundary, conditional-group-exists-fully-empty-boundary, and regression-matrix manifests, and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker continues to make forward progress under the hardened harness, but throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose the current supported frontier and the remaining unsupported surface instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now supports a real but still-bounded subset: literal compile/search/match/fullmatch, cache visibility, `escape()`, collection/replacement helpers, API-level `IGNORECASE`, grouped and named captures, bounded replacement-template and callable replacement workflows, bounded numbered and named backreferences, bounded grouped/nested alternation, bounded branch-local backreferences, one bounded optional-group quantifier slice, one bounded exact-repeat quantified-group slice, one bounded ranged-repeat quantified-group slice, one wider bounded ranged-repeat quantified-group slice, one bounded quantified-alternation slice, one bounded optional-group alternation slice, bounded two-arm, omitted-no-arm, explicit-empty-else, empty-yes-arm, plus fully-empty conditional group-exists slices, one bounded alternation-heavy explicit-empty-else conditional slice, and the first bounded assertion-conditioned conditional compile diagnostics through both module and compiled-`Pattern` entrypoints. The published correctness surface is now `240` cases across `36` manifests with `240` passes and `0` honest gaps after `RBR-0128` moved the first alternation-heavy explicit-empty-else conditional workflows behind the Rust boundary. That still reflects only a bounded subset rather than overall stdlib `re` parity. The active queued frontier is bounded alternation-heavy explicit-empty-else conditional benchmark catch-up in `RBR-0129`, then bounded omitted-no-arm, explicit-empty-else, empty-yes-arm, and fully-empty conditional replacement slices in `RBR-0130` through `RBR-0141`, followed by one bounded omitted-no-arm alternation-heavy conditional slice in `RBR-0142` through `RBR-0144`.

Benchmark publication is still partial by design. The generated status block above carries the current workload and known-gap totals, while the full suite still times the source-tree shim and the built-native path remains a separate six-workload smoke artifact in `reports/benchmarks/native_smoke.json`.

## What The Numbers Mean

The correctness report is honest by construction: `240` passes out of `240` published cases means the currently published slice is fully implemented, not that the repo is near full stdlib `re` parity. Broader conditional replacement plus backtracking-heavy conditional/grouped execution still remain ahead of the frontier, `RBR-0129` is the active benchmark catch-up task, and `RBR-0130` is the next correctness-expansion task.

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
