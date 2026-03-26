## RBR-1400: Move the compiled-pattern wrong-text-model standard definition onto source-tree owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining source-tree-owned compiled-pattern wrong-text-model standard-definition lane from `tests/benchmarks/benchmark_test_support.py`.
- `tests/benchmarks/benchmark_test_support.py` still owns the `"module-workflow-compiled-pattern-wrong-text-model"` `StandardBenchmarkAnchorContractDefinition` even though its selector, correctness-signature builder, workload-signature builder, contract specs, workload loader, and payload-round-trip checks already live on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Move that one standard-definition entry onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so shared benchmark support stops routing this owner lane through `importlib` lambdas and keeps only the genuinely shared compiled-pattern helper definitions.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete the `"module-workflow-compiled-pattern-wrong-text-model"` `StandardBenchmarkAnchorContractDefinition` from `tests/benchmarks/benchmark_test_support.py` so `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS` keeps only the shared literal-success, bounded-wildcard-success, and verbose-bytes-success entries.
- Add the same wrong-text-model standard-definition entry to `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wired directly to the existing owner-local helpers `_is_module_workflow_compiled_pattern_wrong_text_model_workload(...)`, `_module_workflow_compiled_pattern_correctness_case_signature(...)`, and `_module_workflow_compiled_pattern_workload_signature(...)` instead of the current `importlib`-based wrapper lambdas in shared support.
- Keep the existing owner-local wrong-text-model helper surface in `tests/benchmarks/source_tree_benchmark_anchor_support.py` authoritative for this lane; do not re-export those helpers back through `tests/benchmarks/benchmark_test_support.py`.
- Update the benchmark-owner ordering and ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the wrong-text-model standard definition is treated as part of the source-tree owner block rather than the shared compiled-pattern-helper block.
- Keep the existing combined-suite and manifest-validation tests green by consuming the moved owner definition through `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS` without changing benchmark workloads, contract payloads, scorecards, or the remaining collection-replacement and pattern-boundary lanes.
- Do not widen into moving the collection-replacement keyword contract surface, the collection-replacement wrong-text-model selector, or the pattern-boundary wrong-text-model definition family in the same run.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or benchmark_test_support_drops_local_wrong_text_model_contract_builder or compiled_pattern_module_helper_wrong_text_model_selector'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n 'module-workflow-compiled-pattern-wrong-text-model|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the run bounded to this one owner-boundary cleanup.
- Prefer moving the existing definition onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over adding another neutral helper module, another registry layer, or another shared wrapper.
- Do not change benchmark workload files, generated reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1400|RBR-1401|RBR-1402' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only the historical mention inside the completed `RBR-1399` task note, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1400`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I checked the remaining shared compiled-pattern helper definitions in `tests/benchmarks/benchmark_test_support.py`.
  - The literal-success, bounded-wildcard-success, and verbose-bytes-success definitions still rely on genuinely shared owner specs that live in `benchmark_test_support.py`, but the `"module-workflow-compiled-pattern-wrong-text-model"` definition only routes into helpers that already live on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
  - `rg -n 'module-workflow-compiled-pattern-wrong-text-model|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature' tests/benchmarks/benchmark_test_support.py` shows that shared support still mentions this lane only through the standard-definition entry and its routed lambdas.
  - That makes this the next bounded post-JSON architecture task: it deletes one remaining cross-file routing layer from shared benchmark support without widening into the broader collection-replacement or pattern-boundary lanes.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or benchmark_test_support_drops_local_wrong_text_model_contract_builder or compiled_pattern_module_helper_wrong_text_model_selector'` passed with `10 passed, 168 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `3 passed, 115 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `6 passed, 273 deselected in 0.23s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.20s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n 'module-workflow-compiled-pattern-wrong-text-model|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature' tests/benchmarks/benchmark_test_support.py"` currently fails only because the exact shared-support routing layer this task should remove is still present.

## Completion
- Completed 2026-03-26.
- Moved the `module-workflow-compiled-pattern-wrong-text-model` standard benchmark definition out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/source_tree_benchmark_anchor_support.py`, wiring it directly to the existing owner-local selector and signature helpers.
- Updated the benchmark owner-order and export assertions so the wrong-text-model definition is now treated as the first source-tree-owned standard definition rather than part of the shared compiled-pattern helper block.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'standard_benchmark_definitions_keep_owner_blocks_in_order or benchmark_test_support_drops_local_wrong_text_model_contract_builder or compiled_pattern_module_helper_wrong_text_model_selector'` passed with `10 passed, 168 deselected in 0.31s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'compiled_pattern_wrong_text_model_contract_specs_track_manifest_family or source_tree_owner_defines_compiled_pattern_wrong_text_model_surface_locally'` passed with `3 passed, 115 deselected in 0.24s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or compiled_pattern_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `6 passed, 273 deselected in 0.25s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.20s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n 'module-workflow-compiled-pattern-wrong-text-model|_is_module_workflow_compiled_pattern_wrong_text_model_workload|_module_workflow_compiled_pattern_correctness_case_signature|_module_workflow_compiled_pattern_workload_signature' tests/benchmarks/benchmark_test_support.py"` passed.
