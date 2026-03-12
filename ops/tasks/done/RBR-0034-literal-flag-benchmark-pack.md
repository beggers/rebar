# RBR-0034: Add literal-only flag-sensitive boundary benchmarks

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the benchmark harness so the first bounded flag-sensitive helper paths have tiny call-boundary workloads in the published benchmark report once literal-only `IGNORECASE` behavior exists.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/literal_flag_boundary.json`
- `tests/benchmarks/test_literal_flag_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a literal-flag boundary manifest alongside the existing compile-path, module-boundary, regression, pattern-boundary, and collection/replacement manifests without breaking the current report schema.
- The new workload pack includes a bounded set of tiny literal-only `module.search`, `module.match`, `pattern.search`, and `pattern.fullmatch` cases that exercise API-level `IGNORECASE` for both `str` and `bytes`, with cache/provenance labeling that keeps the measurement about public call-boundary cost rather than throughput claims.
- `reports/benchmarks/latest.json` records the new workloads distinctly enough that literal-only flag-sensitive overhead is visible separately from earlier module-boundary and pattern-boundary timing, while still keeping unsupported flag combinations and adapter-mode fallbacks explicit.
- A smoke or unit test regenerates the expanded benchmark report end to end and validates the updated workload/report structure.

## Constraints
- Keep this task on tiny helper-boundary measurements only; do not introduce large-haystack throughput claims, inline-flag benchmarks, or general engine-performance narratives.
- Preserve compatibility with the adapter/provenance work from `RBR-0020` and the bounded honesty contract from `RBR-0032`.
- Do not fabricate benchmark wins for unsupported helper modes or native paths that were not actually exercised.

## Notes
- Build on `RBR-0026` and `RBR-0032`. This task exists so the first supported flag-sensitive helper behavior reaches the published benchmark scorecard quickly instead of staying invisible outside unit tests.
- Added `benchmarks/workloads/literal_flag_boundary.json` with 10 tiny `IGNORECASE` boundary workloads spanning `module.search`, `module.match`, `pattern.search`, and `pattern.fullmatch` across `str` and `bytes`, including two explicit unsupported `IGNORECASE|ASCII` gap rows.
- Extended the benchmark harness default manifest pack so `literal-flag-boundary` publishes alongside the existing compile, module, pattern, collection/replacement, and regression manifests without changing the scorecard schema.
- Added `tests/benchmarks/test_literal_flag_boundary_benchmarks.py` and regenerated `reports/benchmarks/latest.json`; the published benchmark report now covers 45 workloads total, including an 8-measured/2-gap literal-flag manifest and 30 measured `rebar` timings overall.
