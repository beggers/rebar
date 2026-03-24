# RBR-1202: Move compiled-pattern module-helper keyword contract tests onto dedicated suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern module-helper keyword contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated owner in `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`, so the giant combined benchmark suite stops owning another support-module-specific contract surface.

## Deliverables
- `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` so it becomes the owner for the current compiled-pattern module-helper keyword contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertions:
  - `test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements`
  - `test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation`
  - `test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time`
  - `test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads`
  - `test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing`
  - `test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current bool `count` complement coverage and its exact `run_benchmark_workload_with_cpython(...)` outcomes;
  - preserve the current contract-manifest row ordering, `-contract` workload-id rewrite, `use_compiled_pattern` handling, `haystack_text_model is None` expectations, and per-surface payload round-trip assertions;
  - preserve the current callback-time keyword materialization checks, including the existing `_assert_collection_replacement_keyword_kwargs_materialize_on_each_callback_call(...)` path and the exact expected field-name ordering from `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SPEC` and `_COMPILED_PATTERN_MODULE_HELPER_KEYWORD_ERROR_CONTRACT_SPEC`;
  - preserve the current `run_internal_workload_probe(...)` measured-status and positive-`median_ns` assertions for both `cpython.re` and `rebar`; and
  - preserve the current precompile-first callback assertions and the current `TypeError` parity checks against the direct CPython helper route.
- Reuse the existing support and helper modules instead of introducing another abstraction layer:
  - keep using `tests/benchmarks/compiled_pattern_module_helper_keyword_benchmark_support.py` for the contract surfaces and workload params;
  - keep using the existing shared helper imports already available elsewhere in the benchmark tests for callback materialization, workload probing, and source-tree contract workload construction; and
  - do not add a new `*_support.py` module just for this extraction.
- Delete the moved test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not widen it into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'`
- `bash -lc "! rg -n 'test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation|test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads|test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1202` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1202|RBR-1203|RBR-1204" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both the prior architecture cleanup and the current feature task through the normal done path.
- This simplification is still concrete and unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `16078` lines in this run;
  - `rg -n 'test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation|test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads|test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches lines `15022`, `15070`, `15127`, `15158`, `15191`, and `15225`; and
  - `bash -lc "! rg -n 'test_compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements|test_standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation|test_compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time|test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads|test_compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing|test_compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions' tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py"` currently succeeds, confirming the dedicated owner does not already contain this exact block.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_keyword_benchmark_support.py` returned `6 passed in 0.06s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_cases_cover_bool_count_complements or standard_benchmark_manifest_preserves_compiled_pattern_module_collection_replacement_keyword_contract_rows_until_helper_invocation or compiled_pattern_module_helper_collection_replacement_keyword_kwargs_materialize_at_callback_time or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or compiled_pattern_module_helper_keyword_error_callbacks_match_cpython_exceptions'` returned `79 passed, 456 deselected in 0.22s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the moved tests still live in the combined suite.
