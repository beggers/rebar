# RBR-0288: Consolidate the remaining standalone source-tree benchmark scorecard tests

Status: done
Owner: architecture-implementation
Created: 2026-03-14

## Goal
- Replace the remaining standalone source-tree benchmark scorecard tests with one legible, data-driven suite so benchmark report contracts live in one expectation-driven path instead of across repeated subprocess and report-assertion boilerplate.

## Deliverables
- `tests/benchmarks/test_source_tree_benchmark_scorecards.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/report_assertions.py`
- Delete `tests/benchmarks/test_benchmark_smoke.py`
- Delete `tests/benchmarks/test_compile_benchmark_matrix.py`
- Delete `tests/benchmarks/test_regression_benchmark_pack.py`
- Delete `tests/benchmarks/test_post_parser_workflow_benchmarks.py`

## Acceptance Criteria
- The new suite covers the current contracts spread across the four superseded modules: the compile-smoke single-manifest report, the compile-matrix single-manifest report, the curated post-parser three-manifest report, the full regression-pack report, and the smoke-only regression selection.
- Case definitions live in `tests/benchmarks/benchmark_expectations.py` keyed by explicit case ids, with manifest selection derived from the existing benchmark harness path registry in `python/rebar_harness/benchmarks.py` instead of per-file `Path` constants and hand-built subprocess wrappers.
- Shared source-tree benchmark report assertions live in `tests/report_assertions.py` and cover both single-manifest and combined-manifest source-tree scorecards: schema version, phase, adapter metadata, timing path, tracked-report presence, artifact metadata, summary consistency, and cache-mode accounting. Do not leave those assertions duplicated across the new suite.
- `tests/benchmarks/benchmark_expectations.py` stops re-parsing benchmark manifests with its own `json.loads(path.read_text(...))` helper and instead derives raw manifest data through the harness's existing benchmark manifest loader path so tests and the benchmark runner share one manifest/schema interpretation.
- Manifest-specific expectations remain explicit but data-driven. The consolidated suite still pins the known summary totals for each case, the representative measured and known-gap workload ids for compile/post-parser flows, and the regression smoke workload ordering plus manifest-level summary fields that `test_regression_benchmark_pack.py` currently checks.
- After the consolidation lands, none of the four superseded standalone source-tree scorecard modules remain in `tests/benchmarks/`, while `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py`, `tests/benchmarks/test_benchmark_adapter_provenance.py`, `tests/benchmarks/test_built_native_benchmark_smoke.py`, and `tests/benchmarks/test_built_native_full_suite_benchmarks.py` remain intact as specialized coverage.
- The preserved benchmark verification surface still passes with the new suite: `tests.benchmarks.test_source_tree_benchmark_scorecards`, `tests.benchmarks.test_source_tree_combined_boundary_benchmarks`, `tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks`, and `tests.benchmarks.test_benchmark_adapter_provenance`.

## Constraints
- Keep this task scoped to source-tree benchmark test architecture. Do not change benchmark workload manifests, benchmark adapter behavior, built-native benchmark helpers, or the published benchmark report schema to complete it.
- Prefer test-only changes. If a tiny helper outside `tests/` becomes necessary, keep it limited to exposing existing manifest-loading or manifest-order behavior rather than adding a new benchmark abstraction.
- Use ordinary Python expectation tables and shared helpers rather than new JSON manifests, generators, or another custom benchmark harness layer.

## Notes
- These four modules currently total about 533 lines and each reruns the same `python -m rebar_harness.benchmarks` subprocess and scorecard-contract scaffolding with only manifest selections and representative workload ids changing.
- Build on `RBR-0262`: the repeated combined-boundary benchmark wrappers are already consolidated, but the smoke, compile-matrix, regression-pack, and curated post-parser scorecards still sit outside that shared expectation path.
- Leave `tests/benchmarks/test_wider_ranged_repeat_quantified_group_boundary_benchmarks.py` out of scope here; it is a narrow frontier-specific benchmark publication test, not another general benchmark scorecard wrapper.

## Completion Note
- Replaced the four standalone source-tree scorecard wrappers with `tests/benchmarks/test_source_tree_benchmark_scorecards.py`, driven by explicit case ids and manifest selections resolved through `tests/benchmarks/benchmark_expectations.py` and the benchmark harness loader path.
- Expanded `tests/report_assertions.py` so the shared source-tree benchmark contract now covers single-manifest and combined scorecards across `full` and `smoke` selection modes, including artifact metadata, summary/cache accounting, and manifest-selection-aware manifest assertions.
- Deleted `tests/benchmarks/test_benchmark_smoke.py`, `tests/benchmarks/test_compile_benchmark_matrix.py`, `tests/benchmarks/test_post_parser_workflow_benchmarks.py`, and `tests/benchmarks/test_regression_benchmark_pack.py`; their preserved contracts now live in the consolidated suite.
- Verified with `PYTHONPATH=python python3 -m unittest tests.benchmarks.test_source_tree_benchmark_scorecards tests.benchmarks.test_source_tree_combined_boundary_benchmarks tests.benchmarks.test_wider_ranged_repeat_quantified_group_boundary_benchmarks tests.benchmarks.test_benchmark_adapter_provenance`.
