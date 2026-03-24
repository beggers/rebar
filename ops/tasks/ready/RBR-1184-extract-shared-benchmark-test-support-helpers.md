# RBR-1184: Extract shared benchmark test support helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining duplicated generic benchmark test helpers that still live in multiple benchmark owner files by moving them onto one shared test-support module, so the focused support suites and the giant combined benchmark suite stop re-declaring the same temp-manifest writer, expected-exception builder, and numeric-materialization recorder.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark test-support module at `tests/benchmarks/benchmark_test_support.py` for the duplicated generic helper behavior that is currently re-declared in multiple benchmark test files:
  - move the temp-manifest writer into one helper that still writes `textwrap.dedent(...)` output as UTF-8 text under the caller-provided `tmp_path`;
  - move the expected-exception builder into one helper that still maps the current benchmark contract payloads to real `TypeError` and `ValueError` instances using the stored `message_substring`; and
  - move the numeric-materialization recorder into one helper that still monkeypatches `rebar_harness.benchmarks.materialize_numeric_workload_argument(...)`, returns the observed `field_name` list, and preserves the wrapped helper's original return values.
- Delete the duplicated local helper definitions instead of leaving wrappers or aliases behind:
  - remove `_write_test_manifest(...)`, `_expected_exception_instance(...)`, and `_record_numeric_materialization_fields(...)` from `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`;
  - remove `_write_test_manifest(...)` from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`; and
  - remove `_write_test_manifest(...)`, `_expected_exception_instance(...)`, and `_record_numeric_materialization_fields(...)` from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Update the affected benchmark suites to import the shared helper module directly:
  - keep `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` on the same manifest-writing, expected-exception, and numeric-materialization assertions after the extraction;
  - keep `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` on the same manifest-writing contract checks after the extraction; and
  - keep the selected combined-suite cache-contract and compiled-pattern keyword-error tests on the same behavior after the extraction.
- Add one focused support test file at `tests/benchmarks/test_benchmark_test_support.py` that pins the new shared helper module without reintroducing another owner-file dependency:
  - cover one manifest-write case that proves dedenting and UTF-8 writing still happen;
  - cover one expected-exception case for the currently supported payload shapes; and
  - cover one numeric-materialization-recording case that proves field names are collected while the wrapped benchmark helper still returns its original value.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py -k 'preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or module_helper_cache_modes_preserve_expected_purge_and_warmup_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'`

## Constraints
- Keep this cleanup structural and limited to the benchmark test-support layer above. Do not widen it into `python/rebar_harness/benchmarks.py`, benchmark manifest payloads, correctness fixtures, README/reporting surfaces, or tracked ops state prose.
- Prefer one ordinary shared helper module over another private owner-to-owner import or another duplicate local copy.
- Do not turn this into a larger source-tree combined-suite breakup; this task is only the bounded shared-helper extraction above.

## Notes
- `RBR-1184` is the next available unreserved architecture task id in this checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve `RBR-1184`; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is still live and cross-file in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py:47` still defines `_write_test_manifest(...)`, `:57` still defines `_expected_exception_instance(...)`, and `:67` still defines `_record_numeric_materialization_fields(...)`;
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py:32` still defines `_write_test_manifest(...)`; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:176`, `:7793`, and `:15971` still define the same numeric-materialization recorder, temp-manifest writer, and expected-exception builder helpers.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py -k 'preserves_compiled_pattern_module_compile_success_and_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_collection_replacement_success_and_compiled_pattern_module_boundary_success_callbacks_precompile_first_argument_before_timing'` returned `20 passed, 99 deselected` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions or module_helper_cache_modes_preserve_expected_purge_and_warmup_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'` returned `17 passed, 577 deselected` in this run.
