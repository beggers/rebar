# RBR-0008: Scaffold the benchmark harness

Status: ready
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
