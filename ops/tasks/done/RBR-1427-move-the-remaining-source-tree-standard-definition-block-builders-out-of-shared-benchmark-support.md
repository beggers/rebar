## RBR-1427: Move the remaining source-tree standard-definition block builders out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the last source-tree-only standard-definition block builder layer from `tests/benchmarks/benchmark_test_support.py`.
- After `RBR-1426`, the combined source-tree suite still aliases `_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK`, `_compiled_pattern_module_helper_runtime_route(...)`, `_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK`, and `_build_source_tree_standard_benchmark_definitions()` from shared support even though those names are only consumed by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Keep `benchmark_test_support.py` focused on reusable selectors, signature helpers, runtime primitives, and anchor-contract utilities; make the combined source-tree suite own its remaining standard-definition block assembly locally.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining source-tree owner-block assembly surface out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including:
  - `_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK`
  - `_compiled_pattern_module_helper_runtime_route(...)`
  - `_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK`
  - `_build_source_tree_standard_benchmark_definitions()`
- Rewrite the combined source-tree suite to construct `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`, `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, and `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` from its own local owner-block builders instead of aliasing those four names through `benchmark_test_support`.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the tighter boundary:
  - `benchmark_test_support.py` no longer exports the moved owner-block builder names
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved block-builder assignments and helper
  - shared selectors, signature helpers, manifest-path constants, and anchor-contract primitives still remain support-owned
- Keep the run bounded to this owner-boundary cleanup:
  - do not move the underlying shared selector/signature helpers that still have multiple consumers
  - do not change benchmark workloads, `python/rebar_harness/benchmarks.py`, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or source_tree_combined_suite_owns_compiled_pattern_module_compile_standard_definitions or benchmark_test_support_owns_pattern_boundary_surface or benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_route_preserves_expected_shapes'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def _compiled_pattern_module_helper_runtime_route\\(|^def _build_source_tree_standard_benchmark_definitions\\(|^_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK\\s*=|^_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK\\s*=' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, and `.rebar/runtime/dashboard.md` already pointed at `HEAD` `eb65eeae26843893371a0262bcdeed5d38b92be9`, so the runtime counts were not lagging a dirty or older checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1427|RBR-1428|RBR-1429|RBR-1430" ops/state/backlog.md ops/state/current_status.md` returned no matches, so `RBR-1427` was available.
- Candidate selection in this run:
  - `rg -n "benchmark_test_support\\._PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK|benchmark_test_support\\._COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK|benchmark_test_support\\._build_source_tree_standard_benchmark_definitions|benchmark_test_support\\._compiled_pattern_module_helper_runtime_route" tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_benchmark_publication_runtime_contracts.py` showed those four names are only consumed by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `bash -lc "rg -n '^def _compiled_pattern_module_helper_runtime_route\\(|^def _build_source_tree_standard_benchmark_definitions\\(|^_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK\\s*=|^_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK\\s*=' tests/benchmarks/benchmark_test_support.py"` currently finds the exact shared owner-block builder layer this task deletes.
  - I did not widen into a second candidate because this one still removes an entire cross-file ownership seam after the JSON cleanup completed.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or source_tree_combined_suite_owns_compiled_pattern_module_compile_standard_definitions or benchmark_test_support_owns_pattern_boundary_surface or benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_route_preserves_expected_shapes'` passed with `14 passed, 474 deselected in 0.28s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
- Completion note:
  - Moved `_PATTERN_BOUNDARY_STANDARD_DEFINITION_BLOCK`, `_compiled_pattern_module_helper_runtime_route(...)`, and `_COMPILED_PATTERN_MODULE_HELPER_STANDARD_DEFINITION_BLOCK` into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and rewired the source-tree suite to build its local standard-definition surfaces there.
  - Removed those exact owner-only names from `tests/benchmarks/benchmark_test_support.py`, kept the shared selector/signature/helper surface support-owned, and tightened `tests/benchmarks/test_benchmark_test_support.py` to assert the new ownership boundary.
  - Verification passed on the task-local pytest slice, `py_compile`, and the support-file grep check showing the deleted owner-only names are absent from `tests/benchmarks/benchmark_test_support.py`.
