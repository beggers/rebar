## RBR-1399: Move the collection-replacement keyword helper layer out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining collection-replacement keyword helper layer from `tests/benchmarks/benchmark_test_support.py`.
- Shared benchmark support still owns `_collection_replacement_keyword_parameter_name(...)`, `_collection_replacement_positional_keyword_field(...)`, `_is_collection_replacement_keyword_workload(...)`, `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)`, `_is_collection_replacement_compiled_pattern_module_helper_keyword_workload(...)`, and `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` even though the live keyword-contract builders, selectors, and callback-materialization checks are collection-replacement-owner concerns.
- Move that family onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so `tests/benchmarks/benchmark_test_support.py` keeps only the genuinely shared benchmark harness helpers.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Move `_collection_replacement_keyword_parameter_name(...)`, `_collection_replacement_positional_keyword_field(...)`, `_is_collection_replacement_keyword_workload(...)`, `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)`, `_is_collection_replacement_compiled_pattern_module_helper_keyword_workload(...)`, and `_is_collection_replacement_compiled_pattern_keyword_error_workload(...)` out of `tests/benchmarks/benchmark_test_support.py` and into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`.
- Update `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so its standard-definition builders, keyword-error selectors, and keyword-materialization helpers consume that family locally instead of routing through `benchmark_test_support`.
- Update the compiled-pattern module-helper keyword contract surface that remains in `tests/benchmarks/benchmark_test_support.py` so it lazily consumes the moved keyword family from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without re-exporting those moved names back through `benchmark_test_support.py`.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to consume the moved keyword-materialization and keyword-error selectors through the collection-replacement owner module rather than `benchmark_test_support`.
- Rewrite the ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so this keyword helper lane is treated as collection-replacement-owned while leaving the remaining collection-replacement wrong-text-model and compiled-pattern-success lanes scoped exactly as they are today.
- Do not widen into moving `_is_collection_replacement_wrong_text_model_workload(...)`, the compiled-pattern success selector lane, or the broader pattern-boundary helper family.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates or module_helper_collection_replacement_keyword_error_selector_stays_in_scope or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_classifier_helpers or compiled_pattern_module_helper_keyword_contract'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc "! rg -n 'def _collection_replacement_keyword_parameter_name|def _collection_replacement_positional_keyword_field|def _is_collection_replacement_keyword_workload|def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call|def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload|def _is_collection_replacement_compiled_pattern_keyword_error_workload' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Keep the run bounded to this collection-replacement keyword owner-boundary cleanup.
- Prefer moving the existing helper family onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` over introducing another neutral helper module or another routed wrapper layer.
- Do not change benchmark workloads, published reports, generated scorecards, or tracked project-state prose.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1399|RBR-1400|RBR-1401' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only the historical mention inside the completed `RBR-1397` task note, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1399`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I first checked the pattern-boundary wrong-text-model seam, but the current checkout still has no dedicated pattern-boundary owner-support module. Cleaning that lane next would require inventing a new owner module rather than deleting or relocating an existing shared layer, so it is a wider follow-on.
  - I then checked the collection-replacement keyword lane. `rg -n \"_collection_replacement_keyword_parameter_name|_collection_replacement_positional_keyword_field|_is_collection_replacement_keyword_workload|_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call|_is_collection_replacement_compiled_pattern_module_helper_keyword_workload|_is_collection_replacement_compiled_pattern_keyword_error_workload\" ...` shows the definitions still live in `tests/benchmarks/benchmark_test_support.py` while the active consumers are the collection-replacement owner module, its tests, the source-tree combined-suite tests, and the shared compiled-pattern keyword contract surface.
  - That makes the keyword lane the next bounded post-JSON architecture task: it removes one complete collection-owned helper family from shared benchmark support without widening into the remaining wrong-text-model or compiled-pattern-success lanes.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates or module_helper_collection_replacement_keyword_error_selector_stays_in_scope or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'` passed with `14 passed, 141 deselected in 0.15s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_classifier_helpers or compiled_pattern_module_helper_keyword_contract'` passed with `2 passed, 176 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'` passed with `12 passed, 267 deselected in 0.27s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.12s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n 'def _collection_replacement_keyword_parameter_name|def _collection_replacement_positional_keyword_field|def _is_collection_replacement_keyword_workload|def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call|def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload|def _is_collection_replacement_compiled_pattern_keyword_error_workload' tests/benchmarks/benchmark_test_support.py"` currently fails only because the exact shared-support keyword layer this task should remove is still present.

## Completion
- Completed 2026-03-26.
- Moved the collection-replacement keyword helper family onto `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, updated the remaining compiled-pattern module-helper keyword contract surface in `tests/benchmarks/benchmark_test_support.py` to consume that owner surface lazily, and rewrote the affected benchmark ownership tests and direct consumers to use the collection-replacement owner module.
- Verification in this implementation run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'collection_replacement_keyword_contract_surface_routes_owner_names_through_support_alias_without_local_duplicates or module_helper_collection_replacement_keyword_error_selector_stays_in_scope or pattern_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'` passed with `14 passed, 141 deselected in 0.24s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'collection_replacement_classifier_helpers or compiled_pattern_module_helper_keyword_contract'` passed with `2 passed, 176 deselected in 0.34s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_rows_keep_collection_replacement_manifest_measured or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time'` passed with `12 passed, 267 deselected in 0.33s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `2 passed, 62 deselected in 0.12s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc "! rg -n 'def _collection_replacement_keyword_parameter_name|def _collection_replacement_positional_keyword_field|def _is_collection_replacement_keyword_workload|def _assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call|def _is_collection_replacement_compiled_pattern_module_helper_keyword_workload|def _is_collection_replacement_compiled_pattern_keyword_error_workload' tests/benchmarks/benchmark_test_support.py"` passed.
