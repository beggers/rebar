# rebar

`rebar` is an agent-operated Rust regex project with a simple goal: build a bug-for-bug compatible replacement for Python's `re` module that can eventually beat CPython across compile, match, and other common `re` workflows without giving up syntax compatibility, public API behavior, parse-tree correctness, or useful diagnostics.

This repository is run autonomously, but it is meant to be legible to humans first. If you want the short version of what `rebar` is, what exists today, and how far along it is, start with the generated status block below.

<!-- REBAR:STATUS_START -->
## Current State

_Foundation docs, harnesses, and scorecards are in place. The snapshot below focuses on implemented behavior and measured coverage, not long-term ambition._

| Signal | Value |
| --- | --- |
| Phase | Phase 3: implementation and harness bootstrap, with the Rust workspace plus CPython/package scaffolds landed, the Phase 1 parser conformance and compile-path benchmark packs published, the Phase 2 module-boundary benchmark pack and public-API surface scorecard in place, the first Phase 3 match-behavior and regression/stability packs published, the exported-symbol and compiled-pattern scaffolds landed, benchmark adapter/provenance hardening in place, and the remaining correctness and honest-behavior gaps queued. |
| Current milestone | Milestone 2: finish the compiled-pattern correctness slice on top of the landed exported-symbol correctness and benchmark-provenance hardening, then roll directly into the first honest-behavior slice for literal-only matching, compile-cache/purge observability, `escape()` parity, the first literal-only collection/replacement helpers, and their scorecard follow-ons on top of the landed Phase 1 parser conformance and compile-path benchmark packs, verified native-extension smoke path, helper-surface scaffold, exported-symbol scaffold, compiled-pattern scaffold, exact CPython baseline metadata, the Phase 2 public-API correctness scorecard, the first Phase 3 match-behavior smoke pack, the new regression/stability benchmark pack, and benchmark adapter/provenance reporting. |
| Work queue | `10` ready, `0` in progress, `23` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `38` |
| Passing comparisons | `12` |
| Explicit failures | `5` |
| Honest gaps (`unimplemented`) | `21` |
| Covered manifests | `4` |
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

- Land `RBR-0022` so the compiled-pattern scaffold reaches the published correctness scorecard immediately after the exported-symbol pack from `RBR-0021`.
- Use `RBR-0023` through `RBR-0027` as the next slice after that scorecard/provenance wave so the queue turns the landed `Pattern` surface into narrow honest behavior, cache/purge observability, `escape()` parity, pattern-boundary benchmark coverage, and module-workflow correctness.
- Keep `RBR-0028` through `RBR-0031` directly behind the current literal/cache/escape slice so the queue extends from literal-only collection and replacement helpers straight into their correctness and benchmark scorecards instead of stalling after `RBR-0029`.

### Current Risks

- The repo now validates a dedicated built `rebar._rebar` smoke path and the benchmark harness can distinguish shim versus built-native execution modes, but the published benchmark report still reflects the default source-tree shim with `native_module_loaded: false`, so routine measurement paths can still drift away from the verified install/import path.
- The scaffolded Python surface now includes the first helper layer, published match-behavior smoke coverage, CPython-shaped exported flags/constants, and a concrete `Pattern` scaffold, but compiled-pattern correctness coverage and concrete `Match` behavior are still outside the measured compatibility surface.
- The correctness harness now covers 38 published cases across parser, module-API, match-behavior, and exported-symbol layers, but 21 `rebar` comparisons still end in honest `unimplemented` outcomes and there is no compiled-pattern or module-workflow layer yet.
- The benchmark harness now measures 19 published workloads across the compile-path, module-boundary, and regression/stability packs with explicit adapter-mode provenance, but only 2 workloads have real `rebar` timings so compile and match performance claims are still premature and the published suite still exercises the source-tree shim rather than the built native path.
- The project can accidentally optimize for parser internals while missing bug-for-bug `re` module compatibility at the Python surface.
- Long-running supervisor cycles can still delay worker verification and leave runtime state temporarily behind the checked-in harness code.
- Concurrent human and loop commits can still produce diverged git history that requires supervisor resolution; the harness now detects that state accurately but does not auto-rebase it.
- The implementation worker has twenty-one completed delivery tasks under the hardened harness so far, so worker throughput and terminal-state handling still need confirmation across additional cycles.
<!-- REBAR:STATUS_END -->

## Implementation Snapshot

`rebar` has the planning, harness, and reporting foundation in place, but it is still early in the actual regex-engine implementation. Today the repository contains a Rust core crate, a PyO3 extension scaffold, a Python-facing shim, and published correctness and benchmark reports that intentionally expose gaps instead of pretending stdlib `re` compatibility already exists.

On the Python surface, `rebar` now exports CPython-shaped flags, exceptions, and helper types, and `compile()` can return a narrow literal-only `Pattern` scaffold for tiny `str` and `bytes` inputs. Most matching, replacement, and collection behavior is still explicitly unimplemented. The next queue slice is about turning that scaffold into real literal-only `search`/`match`/`fullmatch`, cache visibility, and `escape()` parity.

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
