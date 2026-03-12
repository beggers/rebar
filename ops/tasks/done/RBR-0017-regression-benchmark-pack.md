# RBR-0017: Expand the benchmark harness into a regression and stability pack

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Extend the benchmark harness past the first compile/module suites so it can publish a small curated regression/stability pack and keep a smoke-sized rerun path for future benchmark maintenance.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/regression_matrix.json`
- `tests/benchmarks/test_regression_benchmark_pack.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a regression-oriented workload pack in addition to the compile-path and module-boundary manifests, and it exposes a smoke-sized subset suitable for routine reruns.
- The regression pack includes a small curated mix of parser-stress and module-boundary workloads tied to the tracked specs, with explicit cache-mode/provenance labeling and without claiming engine-throughput wins.
- `reports/benchmarks/latest.json` preserves the existing family breakdown while adding honest regression/stability readiness notes, known-gap accounting, and workload provenance for the new pack.
- A smoke or unit test regenerates the expanded benchmark report end to end and validates the new scorecard structure.

## Constraints
- Keep this task on Phase 3 regression/stability infrastructure only; do not introduce large-haystack throughput claims, CI trend services, or fabricated `rebar` speedups.
- Preserve compatibility with `RBR-0012` and `RBR-0015`; the new workload family should extend the report instead of replacing earlier compile/module suites.
- Keep the curated workload set small enough for one implementation-agent run and fast local verification.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec, especially the Phase 3 regression and stability expansion guidance.
- Build on `RBR-0012` and `RBR-0015`; this task should add durable regression-oriented coverage on top of those suites, not reopen baseline metadata work.

## Completion Notes
- Added `benchmarks/workloads/regression_matrix.json` as a five-workload curated regression/stability pack spanning parser-stress and module-boundary probes, with two smoke-tagged workloads for quick reruns.
- Extended `python/rebar_harness/benchmarks.py` with phase-3 report labeling, per-manifest summaries/provenance, and a `--smoke` mode that filters selected manifests to smoke-tagged workloads.
- Added `tests/benchmarks/test_regression_benchmark_pack.py`, updated existing benchmark summary assertions, and regenerated `reports/benchmarks/latest.json` as a 19-workload combined Phase 3 scorecard.
