## RBR-1269: Move conditional callable and template workload inventories onto collection-replacement support suite

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining collection-replacement workload-id ownership that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so the combined benchmark broker stops defining conditional callable/template inventory constants and a duplicate `_workload_ids_for_text_model(...)` helper that belong beside the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` support surface.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move the duplicate `_workload_ids_for_text_model(...)` helper out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and make `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` the single owner of that helper for collection-replacement workload inventory generation.
- Move these inline conditional callable workload-id inventories out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome them into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS`
  - `_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_CALLABLE_ALTERNATION_WORKLOAD_IDS`
- Move these inline conditional template workload-id inventories out of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and rehome them into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`:
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_BYTES_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_NEGATIVE_COUNT_STR_WORKLOAD_IDS`
  - `CONDITIONAL_GROUP_EXISTS_TEMPLATE_ROUND_TRIP_WORKLOAD_IDS`
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import the moved helper and workload-id tuples from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and delete the local copies.
- Add focused owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` that pins the moved inventory behavior directly:
  - the callable none-count helper-generated `str`/`bytes` workload-id tuples must preserve the current stem expansion order;
  - the callable alternation combined round-trip ordering must stay interleaved as the current first 8 `str`, first 8 `bytes`, trailing 8 `str`, trailing 8 `bytes` sequence;
  - the template round-trip ordering must keep the current bytes-leading, `str` negative-count middle, bytes-trailing shape; and
  - the owner suite must assert that the combined broker imports these constants and `_workload_ids_for_text_model(...)` from the support module instead of redefining them locally.
- Preserve current combined-suite behavior exactly:
  - every existing conditional callable and template manifest/scorecard/round-trip assertion in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` must keep using the same workload ids, tuple ordering, and measured/known-gap expectations; and
  - do not widen this cleanup into broker-local slice expectation helpers such as `_conditional_group_exists_callable_replacement_expectations(...)` or `_conditional_group_exists_template_replacement_expectation(...)`, because those still depend on broker-local `source_tree_combined_slice_expectations(...)` machinery in this checkout.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'not test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'def _workload_ids_for_text_model\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`
- `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_CALLABLE_(BYTES|NEGATIVE_COUNT_(STR|BYTES)|NONE_COUNT_(STR|BYTES|WORKLOAD_IDS)|ALTERNATION_(STR|BYTES|WORKLOAD_IDS))|_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_(BYTES|NEGATIVE_COUNT_STR|ROUND_TRIP)_WORKLOAD_IDS)\\s*=' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the cleanup structural and bounded to the three benchmark files listed above.
- Prefer the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` owner surface over creating another support module, wrapper helper, or imported alias layer.
- Do not move the broker-local conditional callable/template slice expectation helpers in this task; the goal is to delete duplicate workload inventory ownership first, not to widen into a larger broker/slice refactor.

## Notes
- `RBR-1269` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1269|RBR-1270|RBR-1271|RBR-1272" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done -g '*.md'` found no reserved live follow-on ids outside historical mentions in older done-task files.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `9742` lines in this run;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `1282` lines; and
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` is `2691` lines.
- The duplicate helper/inventory ownership is still live in the combined broker in this run:
  - `rg -n 'def _workload_ids_for_text_model\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` matched both files, proving the helper still has duplicate ownership;
  - `rg -n 'CONDITIONAL_GROUP_EXISTS_CALLABLE_|CONDITIONAL_GROUP_EXISTS_TEMPLATE_' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` matched only `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still uses those local inventories in the conditional callable/template round-trip, manifest, and scorecard assertions at lines clustered around `4656`, `4673`, `4709`, `5347`, `5495`, `7031`, `7200`, `7750`, and `7838`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'not test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers'` passed with `51 passed, 1 deselected`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `140 tests collected`.
  - The two negative `rg` checks in `Verification` currently fail because the duplicate helper and inline workload-id inventories still live in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and those failures belong to the exact cleanup queued here.
  - The full `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` file is intentionally not part of this task's acceptance because it currently has one unrelated red test, `test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers`, that expects `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS` to be re-exported from the combined broker even though that attribute is absent in the live checkout before this task lands.

## Completion
- Moved `_workload_ids_for_text_model(...)` plus the conditional callable/template workload-id inventories named in this task into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, and updated `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to import those support-owned symbols instead of redefining them locally.
- Added owner-suite coverage in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` for the callable none-count expansion order, callable alternation interleaving order, template round-trip ordering, and combined-suite import ownership contracts for the moved helper/constants.
- Also re-exported the already support-owned `CONDITIONAL_GROUP_EXISTS_NESTED_CALLABLE_NEGATIVE_COUNT_BYTES_WORKLOAD_IDS` from the combined broker so the existing owner contract test stops failing on that missing attribute.

## Verification Results
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'not test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers'` -> `55 passed, 1 deselected`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'test_conditional_callable_anchor_contract_in_combined_suite_uses_owner_helpers or test_conditional_template_anchor_contract_in_combined_suite_uses_owner_helpers'` -> `2 passed, 54 deselected`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` -> `144 tests collected`
- `bash -lc "! rg -n 'def _workload_ids_for_text_model\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
- `bash -lc "! rg -n '^(CONDITIONAL_GROUP_EXISTS_CALLABLE_(BYTES|NEGATIVE_COUNT_(STR|BYTES)|NONE_COUNT_(STR|BYTES|WORKLOAD_IDS)|ALTERNATION_(STR|BYTES|WORKLOAD_IDS))|_CONDITIONAL_GROUP_EXISTS_CALLABLE_NONE_COUNT_WORKLOAD_STEMS|CONDITIONAL_GROUP_EXISTS_TEMPLATE_(BYTES|NEGATIVE_COUNT_STR|ROUND_TRIP)_WORKLOAD_IDS)\\s*=' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` -> passed
