## RBR-1402: Move the compiled-pattern module-success owner-spec surface onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree contract owner-spec surface from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still defines `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`, and `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` even though those specs build source-tree contract workloads through `tests/benchmarks/source_tree_benchmark_anchor_support.py` and are consumed by the source-tree owner suite.
- Move that one owner-spec surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support keeps only the genuinely shared `CompiledPatternModuleSuccessOwnerSpec` machinery and workload-selector helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`, and `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` from `tests/benchmarks/benchmark_test_support.py`.
- Recreate the same owner-spec surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, reusing the shared `benchmark_test_support.CompiledPatternModuleSuccessOwnerSpec` type plus the existing shared selectors `_is_collection_replacement_compiled_pattern_success_workload(...)`, `_is_module_workflow_compiled_pattern_literal_success_workload(...)`, `_is_module_workflow_compiled_pattern_bounded_wildcard_success_workload(...)`, and `_is_module_workflow_compiled_pattern_verbose_bytes_success_workload(...)`.
- Keep `CompiledPatternModuleSuccessOwnerSpec`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, `include_live_compiled_pattern_module_success_workload(...)`, and the shared selector helpers in `tests/benchmarks/benchmark_test_support.py`; do not widen this run into moving the success dataclass, callback-route helpers, or shared compiled-pattern helper definitions.
- Update `tests/benchmarks/test_benchmark_test_support.py` so the shared-support ownership assertions stop expecting this assignment surface to live in `tests/benchmarks/benchmark_test_support.py`, and update the source-tree owner assertions so the moved surface is treated as source-tree-owned.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/benchmarks/test_benchmark_manifest_validation.py` to consume the moved owner-spec params from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without changing workload selection, contract payloads, measured row counts, or scorecard behavior.
- Keep the run bounded to this one owner-boundary cleanup; do not also move the compiled-pattern compile owner specs, collection-replacement keyword contract surfaces, wrong-text-model helpers, or pattern-boundary support in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_(COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|BOUNDARY_SUCCESS_OWNER_SPEC|SUCCESS_OWNER_SPECS|SUCCESS_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer moving the existing owner-spec assignments onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over adding another neutral helper module, registry, or wrapper layer.
- Do not change benchmark workload files, reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1402' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only a historical mention inside the completed `RBR-1400` task note, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1402`.
- Candidate selection in this run:
  - With both tracked and live JSON counts at zero, I inspected the remaining cross-file support seams under `tests/benchmarks/`.
  - `rg -n '_COMPILED_PATTERN_MODULE_(COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|BOUNDARY_SUCCESS_OWNER_SPEC|SUCCESS_OWNER_SPECS|SUCCESS_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py` still shows the source-tree contract owner-spec assignments living in shared support.
  - The first candidate was viable because the moved surface is already sharply bounded by targeted tests in `tests/benchmarks/test_benchmark_test_support.py`, `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_benchmark_manifest_validation.py`.
  - I did not widen into a second candidate because this one already removes an entire remaining owner-specific assignment layer from shared support.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'` passed with `3 passed, 175 deselected in 0.42s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success'` passed with `6 passed, 113 deselected in 0.23s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'` passed with `43 passed, 236 deselected in 1.00s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'` passed with `2 passed, 62 deselected in 0.19s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "rg -n '_COMPILED_PATTERN_MODULE_(COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|BOUNDARY_SUCCESS_OWNER_SPEC|SUCCESS_OWNER_SPECS|SUCCESS_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"` currently returns the four owner-spec assignments and the param pack in shared support, which is the exact ownership seam this task should remove.

## Completion Note
- Moved `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`, `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`, and `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS` out of `tests/benchmarks/benchmark_test_support.py` and recreated them in `tests/benchmarks/source_tree_benchmark_anchor_support.py` using the shared `CompiledPatternModuleSuccessOwnerSpec` type plus the existing shared workload selectors.
- Updated the shared-support and source-tree owner tests to reflect the new ownership boundary, and repointed the combined boundary and manifest-validation suites to consume the moved source-tree-owned params without changing workload selection or contract behavior.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'` passed with `4 passed, 175 deselected in 0.69s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_module_success'` passed with `6 passed, 113 deselected in 0.50s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or owner_specs_keep_zero_gap_rows_measured'` passed with `43 passed, 236 deselected in 1.17s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_success'` passed with `2 passed, 62 deselected in 0.32s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n '_COMPILED_PATTERN_MODULE_(COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC|BOUNDARY_SUCCESS_OWNER_SPEC|SUCCESS_OWNER_SPECS|SUCCESS_SOURCE_WORKLOAD_PARAMS)' tests/benchmarks/benchmark_test_support.py"` passed.
