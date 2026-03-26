## RBR-1426: Move the remaining pattern-boundary and source-tree standard owner blocks out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining standard benchmark owner-block layer from `tests/benchmarks/benchmark_test_support.py`.
- After `RBR-1423` through `RBR-1425`, shared benchmark support still owns `_compiled_pattern_module_helper_route(...)`, `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`, `_source_tree_standard_benchmark_definitions(...)`, and `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` even though the only real owner lane left is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` plus the meta-tests that police that boundary.
- Keep `benchmark_test_support.py` focused on neutral benchmark utilities, anchor-contract primitives, and helpers with multiple consumers; make the combined source-tree suite own its remaining compiled-pattern-helper, pattern-boundary, and source-tree standard benchmark inventories directly.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/benchmark_test_support.py`

## Acceptance Criteria
- Move the remaining owner-block surface out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, including:
  - `_compiled_pattern_module_helper_route(...)`
  - `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
  - `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`
  - `_source_tree_standard_benchmark_definitions(...)`
  - `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS`
- Rewrite the combined source-tree suite to use those moved local names instead of reaching through `benchmark_test_support` for them.
- Rewrite `tests/benchmarks/test_benchmark_test_support.py` so it verifies the simpler boundary:
  - `benchmark_test_support.py` no longer exports the moved owner-block names
  - `test_source_tree_combined_boundary_benchmarks.py` now owns the moved route helper and standard-definition inventories locally
  - the explicit standard-definition inventory and owner-block ordering checks still pass using the combined suite as the owner of the moved blocks
- Keep the task bounded to those owner-block moves only:
  - do not reopen the compiled-pattern helper keyword-contract surface that still belongs in shared support
  - do not change benchmark workloads, `python/rebar_harness/benchmarks.py`, reports, or tracked project-state files

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or standard_benchmark_param_helpers_require_explicit_definition_inventory or benchmark_test_support_owns_pattern_boundary_surface or benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports or compiled_pattern_module_helper_route_preserves_expected_shapes'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n '^def _source_tree_standard_benchmark_definitions\\(|^SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^def _compiled_pattern_module_helper_route\\(' tests/benchmarks/benchmark_test_support.py"`

## Notes
- Queue and JSON check in this planning run:
  - `.rebar/runtime/dashboard.md` reported `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime JSON counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1426|RBR-1427|RBR-1428" ops/state/backlog.md ops/state/current_status.md` returned no planning-owned reservation for `RBR-1426`.
- Candidate selection in this run:
  - `rg -n "_compiled_pattern_module_helper_route|COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS|PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS|SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS" tests/benchmarks -g '*.py'` showed those names still live in `tests/benchmarks/benchmark_test_support.py`, with the only non-meta consumer path being `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still calls `benchmark_test_support._compiled_pattern_module_helper_route(...)`, while `tests/benchmarks/test_benchmark_test_support.py` still treats the compiled-pattern-helper, pattern-boundary, and source-tree standard benchmark blocks as support-owned inventory.
  - That makes this a bounded post-JSON ownership cleanup: remove one remaining shared owner-block layer rather than continuing to preserve combined-suite-only standard benchmark inventories in the common support module.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or standard_benchmark_param_helpers_require_explicit_definition_inventory or benchmark_test_support_owns_pattern_boundary_surface or benchmark_test_support_owns_compiled_pattern_helper_surface or compiled_pattern_module_helper_standard_owner_surface_surviving_suites_import_source_tree_exports or compiled_pattern_module_helper_route_preserves_expected_shapes'` passed with `15 passed, 470 deselected in 0.29s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n '^def _source_tree_standard_benchmark_definitions\\(|^SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS\\s*=|^def _compiled_pattern_module_helper_route\\(' tests/benchmarks/benchmark_test_support.py"` currently finds the exact shared owner-block surface this task deletes.
