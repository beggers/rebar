## RBR-1237: Collapse collection-replacement keyword contract support onto owned suites

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the standalone `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py` layer now that it is only a test-support broker between the dedicated collection-replacement keyword contract suite and the compiled-pattern helper keyword suite. The dedicated owner test should keep the local keyword-contract builders and selectors it is the only consumer of, while the one genuinely shared callback-materialization helper should live on the existing shared benchmark test-support surface instead of behind a separate module.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`

## Acceptance Criteria
- Delete the standalone broker module:
  - remove `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`; and
  - update benchmark test imports so no `tests/benchmarks/*` file still imports it.
- Move the genuinely shared callback-time numeric-materialization helper onto the shared benchmark test-support owner:
  - move `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)` onto `tests/benchmarks/benchmark_test_support.py`;
  - keep it implemented in terms of the existing `_record_numeric_materialization_fields(...)` helper there; and
  - add focused coverage in `tests/benchmarks/test_benchmark_test_support.py` that proves the moved helper still records the expected field names across both success and `TypeError` callback paths.
- Rehome the collection-replacement-only keyword-contract plumbing onto its dedicated owner suite instead of keeping it in a separate support module:
  - move `_pattern_helper_collection_replacement_keyword_error_workload(...)`;
  - move `_is_collection_replacement_pattern_helper_keyword_error_workload(...)`;
  - move `_assert_keyword_error_workload_probe_measured(...)`;
  - move `_is_collection_replacement_module_helper_keyword_error_workload(...)`;
  - move `_PATTERN_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`; and
  - move `_MODULE_HELPER_KEYWORD_ERROR_SOURCE_WORKLOADS`
  into `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`.
- Update the compiled-pattern helper keyword suite to consume only the shared helper from `tests/benchmarks/benchmark_test_support.py`:
  - `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` must no longer depend on the deleted broker module; and
  - do not make benchmark test files import helpers from other benchmark test files.
- Preserve the current bounded benchmark-contract behavior exactly:
  - the pattern-helper keyword-error rows selected from `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the module-helper keyword-error rows selected across `benchmarks/workloads/module_boundary.py` and `benchmarks/workloads/collection_replacement_boundary.py` must stay identical and in the same order;
  - the callback-time materialized field-name expectations for `maxsplit`, `count`, and keyword aliases must remain unchanged; and
  - the CPython exception-text comparisons and internal workload-probe expectations must stay on the current exact helper paths.
- Do not widen this cleanup into workload manifests, `python/rebar_harness/benchmarks.py`, runtime-contract owners, reports, README text, or tracked ops state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `bash -lc "! test -e tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py"`

## Constraints
- Keep the cleanup structural and bounded to the benchmark test-support/test layer above.
- Prefer moving code onto the existing owner surfaces over introducing another shared helper module or keeping compatibility aliases.
- Preserve the current workload-id ordering, drift-assertion messages, callback semantics, and exact CPython exception text checks.

## Notes
- `RBR-1237` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live task files;
  - the highest filed task is `RBR-1236`; and
  - `rg -n "RBR-1237|RBR-1238|RBR-1239|RBR-1240|RBR-1241|RBR-1242" ops/state/current_status.md ops/state/backlog.md` returned no reserved follow-on ids in this range.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is concrete in the live checkout:
  - `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py` is only `227` lines and defines five helper functions plus two source-workload tuples;
  - `rg -n "collection_replacement_keyword_contract_benchmark_support" tests/benchmarks` matches only two import sites: the dedicated owner suite `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py` and the compiled-pattern helper keyword suite `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`; and
  - `tests/benchmarks/benchmark_test_support.py` already owns `_record_numeric_materialization_fields(...)`, making it the natural shared home for the only remaining cross-suite helper in this broker module.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` passed with `193 passed`.
  - `bash -lc "! test -e tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py"` currently fails because the broker module still exists, and that failure belongs to the exact cleanup queued here.

## Completion
- Moved `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)` onto `tests/benchmarks/benchmark_test_support.py` and added focused success/error-path coverage in `tests/benchmarks/test_benchmark_test_support.py`.
- Rehomed the collection-replacement-only workload builders, selectors, source-workload tuples, and probe helper into `tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py`, preserving the existing source-workload ordering and probe behavior.
- Updated `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` to import only the shared callback helper from the shared benchmark support surface and deleted `tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_collection_replacement_keyword_contract_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` -> `195 passed`
  - `bash -lc "! test -e tests/benchmarks/collection_replacement_keyword_contract_benchmark_support.py"`
