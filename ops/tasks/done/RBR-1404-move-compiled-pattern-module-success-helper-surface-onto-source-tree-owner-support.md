## RBR-1404: Move the compiled-pattern module-success helper surface onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-owned compiled-pattern module-success helper surface from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still defines `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`, and `include_live_compiled_pattern_module_success_workload(...)` even though that surface is only consumed by `tests/benchmarks/source_tree_benchmark_anchor_support.py` and the source-tree benchmark/manifest-validation suites.
- Move that one helper surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only genuinely shared primitives and selectors instead of a source-tree-only contract lane.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`, and `include_live_compiled_pattern_module_success_workload(...)` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate that helper surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wired to the existing shared primitives it still needs, without changing the moved surface's behavior, contract payloads, workload selection, or measured-row expectations.
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to instantiate the moved owner-spec class locally instead of importing it from shared support.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the shared-support ownership assertions stop treating that module-success helper surface as benchmark-support-owned, and add or adjust source-tree-owner assertions so the moved class and helper functions are treated as source-tree-owned.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/benchmarks/test_benchmark_manifest_validation.py` to call the moved helper surface from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without changing benchmark results.
- Keep the run bounded to this one owner-boundary cleanup; do not also move the shared compiled-pattern selector helpers, `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, collection-replacement helpers, or unrelated source-tree scorecard machinery in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success_surface or source_tree_support_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_contract_builder_surface_uses_one_owned_route'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n '^(class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest|def include_live_compiled_pattern_module_success_workload)' tests/benchmarks/benchmark_test_support.py"`

## Completion
- Moved `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)`, and `include_live_compiled_pattern_module_success_workload(...)` from `tests/benchmarks/benchmark_test_support.py` onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Updated the source-tree owner specs to instantiate the local class and updated the benchmark-support, source-tree-support, combined-boundary, and manifest-validation tests to treat the moved surface as source-tree-owned.
- Verification passed:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success_surface or source_tree_support_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_contract_builder_surface_uses_one_owned_route'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
  - `bash -lc "! rg -n '^(class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest|def include_live_compiled_pattern_module_success_workload)' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer moving the existing source-tree-only helper surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over adding another neutral helper module, registry, or wrapper layer.
- Do not change benchmark workload files, reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1404|1404' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` found no reserved future-id use and no ready/in-progress/blocked duplicate for `RBR-1404`.
- Candidate selection in this run:
  - With both tracked and live JSON counts at zero, I inspected the remaining benchmark-support ownership seams under `tests/benchmarks/`.
  - `rg -n 'CompiledPatternModuleSuccessOwnerSpec|_assert_compiled_pattern_module_success_payload_round_trip|_assert_compiled_pattern_success_rows_measured_in_combined_manifest|include_live_compiled_pattern_module_success_workload' tests/benchmarks -g '*.py'` shows this helper surface still lives in `tests/benchmarks/benchmark_test_support.py` and is consumed by source-tree owner files and their tests.
  - `bash -lc "rg -n '^(class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest|def include_live_compiled_pattern_module_success_workload)' tests/benchmarks/benchmark_test_support.py"` currently returns the four shared-support definitions, which is the exact ownership seam this task should remove.
  - I did not widen into another candidate because this one removes a remaining cross-file owner-specific helper layer from shared benchmark support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success_surface or source_tree_support_owns_compiled_pattern_module_success_owner_specs or compiled_pattern_contract_builder_surface_uses_one_owned_route'` passed with `3 passed, 177 deselected in 0.31s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'` passed with `6 passed, 114 deselected in 0.22s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'` passed with `2 passed, 62 deselected in 0.20s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'` passed with `43 passed, 236 deselected in 0.97s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
