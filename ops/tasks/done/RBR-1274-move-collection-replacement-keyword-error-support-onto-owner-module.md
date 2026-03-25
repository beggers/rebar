## RBR-1274: Move collection-replacement keyword-error support onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining collection-replacement keyword-error support surface that still lives inside `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, so the collection-replacement benchmark layer keeps workload builders, selector logic, manifest paths, and live source-workload inventories in its existing owner support module instead of in a 2485-line test file.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` so it becomes the single owner of the collection-replacement keyword-error support surface currently defined in the test module:
  - `COLLECTION_REPLACEMENT_MANIFEST_PATH`
  - `MODULE_BOUNDARY_MANIFEST_PATH`
  - `_pattern_helper_collection_replacement_keyword_error_workload(...)`
  - `_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS`
  - `_is_collection_replacement_pattern_helper_keyword_error_workload(...)`
  - `_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
  - `_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS`
  - `_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS`
  - `_is_collection_replacement_module_helper_keyword_error_workload(...)`
  - `_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
- Update `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` to import and use that support-owned surface instead of defining the manifest-path constants, workload builder, selectors, and source-workload tuples locally.
- Preserve current behavior exactly:
  - keep the same collection-replacement and module-boundary manifest paths;
  - keep the same pattern-helper and module-helper keyword-error workload ids, ordering, and drift messages;
  - keep `_pattern_helper_collection_replacement_keyword_error_workload(...)` producing the same manifest id, timing scope, kwargs payload shape, expected-exception round-trip behavior, and text-model handling as before; and
  - keep the existing keyword-materialization assertions, workload-probe checks, and CPython exception matching behavior unchanged apart from importing the support-owned surface.
- Keep the cleanup structural and bounded to the two files above. Do not widen it into `python/rebar_harness/benchmarks.py`, workload manifests under `benchmarks/workloads/`, other benchmark suites, reports, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `bash -lc "! rg -n 'def _pattern_helper_collection_replacement_keyword_error_workload\\(|def _is_collection_replacement_pattern_helper_keyword_error_workload\\(|def _is_collection_replacement_module_helper_keyword_error_workload\\(|^COLLECTION_REPLACEMENT_MANIFEST_PATH\\s*=|^MODULE_BOUNDARY_MANIFEST_PATH\\s*=|_PATTERN_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS\\s*=|_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS\\s*=|_MODULE_HELPER_BOUNDARY_KEYWORD_ERROR_WORKLOAD_IDS\\s*=|_MODULE_HELPER_COLLECTION_REPLACEMENT_KEYWORD_ERROR_WORKLOAD_IDS\\s*=|_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS\\s*=' tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py"`

## Constraints
- Prefer consolidating onto the existing `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` owner module over creating another helper/support file. The point is to finish the ownership move, not to add a fresh abstraction layer.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`.
- Do not change keyword-error workload selection, callback materialization behavior, workload-probe semantics, or assertion coverage in this task.

## Notes
- `RBR-1274` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1274|RBR-1275|RBR-1276|RBR-1277|RBR-1278" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The ownership drift is concrete in the live checkout:
  - `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` is `2485` lines in this run and still defines the keyword-error manifest-path constants, workload builder, selectors, and source-workload inventories locally;
  - `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` is `1404` lines and already owns the adjacent collection-replacement keyword selector surface that these keyword-error helpers depend on; and
  - `rg -n "_pattern_helper_collection_replacement_keyword_error_workload|_is_collection_replacement_pattern_helper_keyword_error_workload|_is_collection_replacement_module_helper_keyword_error_workload|_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS|COLLECTION_REPLACEMENT_MANIFEST_PATH|MODULE_BOUNDARY_MANIFEST_PATH" tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` still matches those local support definitions and uses in this run.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` passed with `100 passed`; and
  - the negative `rg` check in `Verification` currently fails because that support surface still lives in `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, and that failure belongs to the exact cleanup queued here.
- Completion note:
  - Moved the collection-replacement keyword-error manifest constants, workload builder, selector helpers, workload id tuples, and source-workload inventories into `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`, then updated `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` to import that owner-owned surface directly.
  - Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` (`100 passed`) and with the negative `rg` contract in `Verification`, which now succeeds.
