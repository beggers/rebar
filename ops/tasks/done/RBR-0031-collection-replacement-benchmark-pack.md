# RBR-0031: Add collection and replacement boundary benchmarks

Status: done
Owner: implementation
Created: 2026-03-12
Completed: 2026-03-12

## Goal
- Extend the benchmark harness so the first literal-only collection and replacement helpers have tiny call-boundary workloads in the published benchmark report once they stop being placeholders.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/collection_replacement_boundary.json`
- `tests/benchmarks/test_collection_replacement_boundary_benchmarks.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The benchmark runner can execute a collection/replacement boundary manifest alongside the existing compile-path, module-boundary, regression, and pattern-boundary manifests without breaking the current report schema.
- The new workload pack includes a bounded set of tiny literal-only `module.split`, `module.findall`, `module.sub`, `pattern.finditer`, and `pattern.subn` cases over `str` and `bytes` inputs, with adapter/cache labeling that keeps the measurement about public call-boundary cost rather than throughput claims.
- `reports/benchmarks/latest.json` records the new workloads distinctly enough that collection/replacement helper overhead is visible separately from earlier module-boundary and precompiled-pattern timing, while still keeping unsupported operations and adapter-mode fallbacks explicit.
- A smoke or unit test regenerates the expanded benchmark report end to end and validates the updated workload/report structure.

## Constraints
- Keep this task on tiny helper-boundary measurements only; do not introduce large-haystack throughput claims, replacement-template benchmarks, or broad engine-performance narratives.
- Preserve compatibility with the adapter/provenance work from `RBR-0020` and the bounded honesty contract from `RBR-0028` and `RBR-0029`.
- Do not fabricate benchmark wins for unsupported helper modes or native paths that were not actually exercised.

## Notes
- Build on `RBR-0026`, `RBR-0028`, and `RBR-0029`; this task exists so the first honest collection/replacement helper behavior reaches the published benchmark scorecard quickly instead of staying invisible outside unit tests.
- Added `benchmarks/workloads/collection_replacement_boundary.json` with 10 tiny literal-only `str` and `bytes` workloads spanning `module.split`, `module.findall`, `module.sub`, `pattern.finditer`, and `pattern.subn`, plus smoke labels and cache/provenance notes.
- Extended `python/rebar_harness/benchmarks.py` so the workload model carries replacement/count/maxsplit metadata, the default combined suite includes the new manifest, `finditer()` workloads eagerly consume iterator results, and the adapter dispatch supports the new collection/replacement operations without changing the report schema.
- Added `tests/benchmarks/test_collection_replacement_boundary_benchmarks.py` and regenerated `reports/benchmarks/latest.json`; the published benchmark report now covers 35 workloads total, including a fully measured 10-workload `collection-replacement-boundary` manifest and 22 measured `rebar` timings overall.
