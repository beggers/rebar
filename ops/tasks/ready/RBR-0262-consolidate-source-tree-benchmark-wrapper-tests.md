# RBR-0262: Consolidate the source-tree benchmark wrapper tests into one data-driven suite

Status: ready
Owner: feature-implementation
Created: 2026-03-13

## Goal
- Replace the repeated source-tree combined-suite benchmark wrapper tests with one legible, data-driven benchmark contract suite so the benchmark harness is asserted in one place instead of across dozens of near-identical files.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/benchmark_expectations.py`
- `tests/report_assertions.py`
- Delete the superseded manifest-specific source-tree wrapper modules under `tests/benchmarks/` that currently restate the combined `--manifest` list, while keeping `test_benchmark_smoke.py`, `test_compile_benchmark_matrix.py`, `test_post_parser_workflow_benchmarks.py`, `test_benchmark_adapter_provenance.py`, `test_built_native_benchmark_smoke.py`, and `test_built_native_full_suite_benchmarks.py`

## Acceptance Criteria
- The new suite covers the existing manifest-specific combined-source-tree contracts now spread across the 28 wrapper files named `test_*_boundary_benchmarks.py`.
- The consolidated test path derives its selected manifest lists from `python/rebar_harness/benchmarks.py` and its existing ordered `DEFAULT_MANIFEST_PATHS` instead of restating the full combined `--manifest` argument list in each test file.
- Common report-contract assertions for the source-tree benchmark path live in shared helpers rather than being recopied per manifest: schema version, phase, implementation adapter metadata, timing path, tracked-report presence, combined artifact metadata, and summary consistency.
- Manifest-specific expectations remain explicit but data-driven by manifest id: each contract still checks its manifest summary, stored smoke ids, representative measured workloads, and representative known-gap workloads without requiring a dedicated standalone test module per manifest.
- The specialized benchmark tests that are not part of the repeated wrapper pattern remain intact and readable: smoke, compile-matrix, post-parser workflow, adapter provenance, built-native smoke, and built-native full-suite.
- The resulting benchmark test layout removes the repeated wrapper boilerplate rather than moving it into another large pile of copied constants; there should be no remaining per-manifest source-tree benchmark file that hard-codes the full combined manifest list.

## Constraints
- Keep this task scoped to benchmark test architecture. Do not change benchmark workload manifests, benchmark adapter behavior, or the published report schema to complete it.
- Prefer test-only changes; if a tiny helper is needed outside `tests/`, keep it limited to exposing existing benchmark-manifest ordering rather than adding new benchmark concepts.
- Preserve the current source-tree benchmark coverage surface and assertion depth; this is a simplification task, not a reduction in benchmark contract checking.

## Notes
- Today the 28 repeated wrapper files account for roughly 9k lines of test code and restate about 490 `--manifest` arguments even though the ordering already exists in `rebar_harness.benchmarks.DEFAULT_MANIFEST_PATHS`.
- Queue this after the current `RBR-0251` through `RBR-0261` frontier; it is worthwhile simplification work, but not an immediate prerequisite for the next regex slice.
