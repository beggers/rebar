# RBR-0015: Expand the benchmark harness into a module-boundary suite

Status: done
Owner: implementation
Created: 2026-03-11

## Goal
- Extend the benchmark harness past compile-only measurements so it can publish the first module-boundary timings for import and helper-call overhead at the `re`-compatible surface.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/module_boundary.json`
- `tests/benchmarks/test_module_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a module-boundary workload pack in addition to the existing compile-path manifest.
- The new workload pack includes representative `re`-surface cases such as import cost plus small helper-call paths with explicit cache-state labels where relevant; use tiny inputs so the measurements stay about boundary overhead rather than engine throughput.
- `reports/benchmarks/latest.json` distinguishes compile-path results from module-boundary results and records honest `rebar` status for unimplemented helpers instead of fabricating timings or speedups.
- A smoke or unit test regenerates the expanded benchmark report and validates the new scorecard structure end to end.

## Constraints
- Keep this task on Phase 2 module-boundary benchmarking only; do not add large-haystack engine-throughput claims.
- Preserve compatibility with the exact-baseline metadata work from `RBR-0009` and the compile-path suite from `RBR-0012`; the new workload family should extend the report, not replace earlier results.
- Do not hide missing helper behavior behind stdlib fallback paths or blended aggregates.

## Notes
- Use `docs/benchmarks/plan.md` as the primary task spec, especially the Phase 2 module-boundary suite guidance.
- Build on `RBR-0012` and `RBR-0013`; the benchmark suite should exercise the actual scaffolded module surface the repo exposes at that point.

## Completion
- Completed 2026-03-11.
- Generalized `python/rebar_harness/benchmarks.py` to load one or more manifests, execute compile-path plus module-boundary operations, and emit a combined scorecard that keeps parser and module families distinct.
- Added `benchmarks/workloads/module_boundary.json` with cold import, module-level compile/search/match helper workloads, and explicit cold/warm/purged cache labels where they apply.
- Added `tests/benchmarks/test_module_boundary_benchmarks.py` and regenerated `reports/benchmarks/latest.json`; the published report now contains both the six-workload parser compile pack and the eight-workload module-boundary pack, with honest `rebar` unimplemented results for helper calls.
- Follow-up note for supervisor: `RBR-0020` should still harden per-run provenance beyond the current scorecard-level `timing_path` metadata, especially once built-native benchmark execution is introduced.
