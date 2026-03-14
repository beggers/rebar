# rebar

`rebar` is a Rust-backed attempt at a bug-for-bug compatible replacement for Python's `re` module. The target is simple: match CPython's accepted syntax, public API behavior, parse trees, and diagnostics first, then compete on compile and match speed through a CPython-facing extension.

The repo runs through an agent loop, but the landing page stays human-first. Start with the status block for the current published slice, how much of it is measured, and what still blocks broader claims.

<!-- REBAR:STATUS_START -->
## Current State

_This block reports the implemented slice and measurement coverage, not estimated end-state parity._

| Signal | Value |
| --- | --- |
| Phase | Phase 3 is still a bounded Rust-backed subset: published correctness is fully passing through the broader `{1,4}` grouped backtracking-heavy slice, while published benchmark coverage still stops one bounded slice earlier. |
| Delivery estimate | The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity. Benchmark coverage is still catching up to the newest correctness slice, and broad performance claims remain premature. |
| Current milestone | Milestone 2 has the broader `{1,4}` grouped backtracking-heavy slice at Rust-backed parity; next up is catching that same bounded workflow up on the Python-path benchmark surface. |
| Work queue | `2` ready, `0` in progress, `286` done, `0` blocked |
| Foundation tracks | `10/10` landed (`[##################] 100%`) |

### Correctness Snapshot

| Metric | Value |
| --- | --- |
| Published cases | `729` |
| Passing in published slice | `729` |
| Explicit failures | `0` |
| Honest gaps (`unimplemented`) | `0` |
| Covered manifests | `82` |
| Source | [`reports/correctness/latest.json`](reports/correctness/latest.json) |

_These correctness counts cover only the published slice. Overall delivery estimate: The repo has the right harness and reporting shape, but it is still far from drop-in `re` parity. Benchmark coverage is still catching up to the newest correctness slice, and broad performance claims remain premature._

### Benchmark Snapshot

| Metric | Value |
| --- | --- |
| Baseline | CPython 3.12.3 (module `re`, exe `/usr/bin/python3`) |
| Published workloads | `473` |
| Workloads with real `rebar` timings | `442` |
| Known-gap workloads | `31` |
| Timing path | `source-tree-shim` |
| Source | [`reports/benchmarks/latest.json`](reports/benchmarks/latest.json) |

_Full-suite benchmark publication still runs through the source-tree shim; strict built-native sidecars are checked in separately at [`reports/benchmarks/native_full.json`](reports/benchmarks/native_full.json) for the latest built-native full-suite run and [`reports/benchmarks/native_smoke.json`](reports/benchmarks/native_smoke.json) for the smoke slice._

_README speedup rollups stay omitted while only `442` of `473` published workloads have real `rebar` timings._

### Immediate Next Steps

- Land `RBR-0278` to catch the broader `{1,4}` grouped backtracking-heavy slice up on the Python-path benchmark surface.

### Current Risks

- The main published benchmark report still measures the source-tree shim rather than the built-native extension path.
- The newly landed broader `{1,4}` grouped backtracking-heavy slice is not yet on the published benchmark surface, so the fully passing and fully measured frontier still stops one bounded slice earlier.
<!-- REBAR:STATUS_END -->

## What Exists Today

`rebar` already has a real Rust core, a CPython-facing extension boundary, and canonical correctness and benchmark reports. It is still an early, narrow `re` subset rather than a drop-in replacement.

The published correctness slice is clean, but the benchmark story is still catch-up work on that same bounded frontier and the main report still runs through the source-tree shim. Near term, the project is finishing Python-path benchmark coverage for the latest Rust-backed `{1,4}` grouped backtracking-heavy slice before widening the frontier again.

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
