# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The repo runs through an agent loop, but the landing page stays human-first. Start with the status block for the current published slice, how much of it is measured, and what still blocks broader claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is widening a bounded Rust-backed `re` slice; the tracked fully passing frontier now reaches the broader `{1,4}` grouped-conditional slice, but overall parity is still narrow. |
| Delivery estimate | Foundation and reporting are in place. The tracked correctness frontier is fully passing and the Python-path benchmark report is caught up with that published slice, but the project is still far from drop-in parity and not ready for speed claims. |
| Current milestone | Milestone 2 has the broader `{1,4}` grouped-conditional slice landed behind `rebar._rebar` and caught up on the Python-path benchmark surface; next up is the adjacent broader `{1,4}` grouped backtracking-heavy slice through publication and parity. |
| Work queue | `1` ready, `0` in progress, `278` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `715` |
| Passing in published slice | `715` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `82` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: Foundation and reporting are in place. The tracked correctness frontier is fully passing and the Python-path benchmark report is caught up with that published slice, but the project is still far from drop-in parity and not ready for speed claims._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `467` |
| Workloads with real `rebar` timings | `436` |
| Known-gap workloads | `31` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `436` of `467` published workloads have real `rebar` timings._

### Immediate Next Steps

- Publish the adjacent broader `{1,4}` grouped backtracking-heavy slice, then convert that same bounded workflow to Rust-backed parity.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The adjacent broader `{1,4}` grouped backtracking-heavy slice is queued next but not yet published or Rust-backed, so the tracked frontier still stops short of that overlapping-branch workflow.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and published correctness and benchmark reports. What it does not have yet is broad `re` coverage: the current correctness frontier is fully passing, the benchmark report still trails that frontier, and the supported slice is still small relative to stdlib `re`.

Benchmarking is useful as a coverage signal, not a performance victory lap yet. The main published suite still runs through the source-tree shim, and the built-native numbers live in separate sidecars, so the README avoids headline speedups and treats benchmark counts as coverage, not proof of speed.

## How To Read It

Treat the correctness counts as "the documented frontier matches CPython on this slice," not as a claim of broad drop-in compatibility. Treat the benchmark counts as "this much of that slice is measured through the public Python path," not as proof that `rebar` is already faster than stdlib `re`.

## Where To Look

For detailed project state, start with `ops/state/current_status.md` and `ops/state/backlog.md`. For the published scorecards, use `reports/correctness/latest.json`, `reports/benchmarks/latest.json`, `reports/benchmarks/native_full.json`, and `reports/benchmarks/native_smoke.json`. For the operating model and queue layout, `ops/README.md` is the canonical reference.

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
