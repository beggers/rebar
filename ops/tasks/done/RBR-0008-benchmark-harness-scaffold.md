# RBR-0008: Scaffold the benchmark harness

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Create the first runnable benchmark harness skeleton and publish an initial placeholder benchmark scorecard.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/compile_smoke.json`
- `tests/benchmarks/test_benchmark_smoke.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The harness can load a small workload manifest and execute at least one compile-path smoke workload against baseline CPython stdlib `re`.
- The `rebar` side is represented by an explicit adapter boundary that records unavailable or unimplemented candidate timings honestly instead of fabricating benchmark wins.
- `reports/benchmarks/latest.json` uses the top-level scorecard shape from `docs/benchmarks/plan.md` and includes baseline metadata, environment metadata, summary fields, and per-workload records.
- A smoke test or documented command exercises the benchmark runner end to end and regenerates the tracked scorecard.

## Constraints
- Keep this to the Phase 0 benchmark skeleton from the plan; do not build a large workload corpus or make publishable performance claims yet.
- Focus on compile-path and module-boundary scaffolding only; regex execution throughput remains deferred.
- Keep the initial baseline aligned with the CPython `3.12.x` family until the runner can record an exact patch/build.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec.
- Use `docs/spec/drop-in-re-compatibility.md` and `docs/spec/syntax-scope.md` to keep workload categories aligned with the intended parser and module surfaces.
- Keep the harness layout compatible with the correctness scaffold from `docs/testing/correctness-plan.md` so shared adapters and report helpers can emerge later.

## Completion
- Added `python/rebar_harness/benchmarks.py` as a Phase 0 benchmark runner with a versioned workload manifest loader, CPython/rebar compile adapters, environment metadata capture, and machine-readable scorecard output.
- Added `benchmarks/workloads/compile_smoke.json` with two parser-family compile smoke workloads that keep cold-versus-warm cache labels visible without claiming broader coverage.
- Published `reports/benchmarks/latest.json` with measured CPython baseline timings plus explicit `rebar` `unimplemented` benchmark records instead of fabricated implementation numbers.
- Added `tests/benchmarks/test_benchmark_smoke.py` and verified the scaffold with `PYTHONPATH=python python3 -m rebar_harness.benchmarks`, `python3 -m unittest tests.benchmarks.test_benchmark_smoke`, and the existing correctness/import/reporting smoke tests.

## Follow-Up Notes
- `RBR-0012` should expand the manifest beyond the current parser compile proxy workloads and add module-boundary benchmark families once the `rebar` side can expose real timings.
