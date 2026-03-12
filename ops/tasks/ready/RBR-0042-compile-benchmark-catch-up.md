# RBR-0042: Convert compile-path benchmarks from scaffold-only toward partial measurement

Status: ready
Owner: implementation
Created: 2026-03-12

## Goal
- Update the compile-path benchmark pack so newly supported parser-matrix compile cases produce real `rebar` timings instead of leaving the manifest effectively scaffold-only after parser parity lands.

## Deliverables
- `python/rebar_harness/benchmarks.py`
- `benchmarks/workloads/compile_matrix.json`
- `tests/benchmarks/test_compile_benchmark_matrix.py`
- `reports/benchmarks/latest.json`

## Acceptance Criteria
- The compile-path benchmark runner records real `rebar` timings for the compile workloads whose patterns are now supported by the bounded parser tasks through `RBR-0041`, while leaving still-unsupported workloads explicit as known gaps.
- `reports/benchmarks/latest.json` no longer leaves the compile-matrix manifest effectively unchanged from the earlier scaffold-only state once supported compile cases exist; the report should show partial measurement honestly rather than fabricating full coverage.
- Unit or smoke coverage regenerates the compile benchmark report end to end and validates the updated workload/report expectations without regressing the existing adapter/provenance metadata.

## Constraints
- Keep this task scoped to compile-path benchmark catch-up for already-supported parser cases; do not introduce large-haystack execution benchmarks, native-only publication requirements, or broad benchmark-schema churn.
- Do not fabricate benchmark wins for unsupported compile paths or execution modes that were not actually exercised.
- Preserve the existing source-tree-shim versus built-native provenance reporting from `RBR-0020`.

## Notes
- Build on `RBR-0037` through `RBR-0041`. This task exists so benchmark reporting follows newly landed parser support instead of remaining one milestone behind the correctness surface.
