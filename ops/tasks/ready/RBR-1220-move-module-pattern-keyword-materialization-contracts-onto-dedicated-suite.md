# RBR-1220: Move module-pattern keyword materialization contracts onto dedicated suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining generic module/pattern keyword normalization and callback-time materialization contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing keyword owner in `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`, so the giant combined benchmark suite stops owning another generic keyword-contract surface.

## Deliverables
- `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` so it becomes the owner for the current module/pattern keyword normalization and callback-time materialization contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertion surfaces:
  - `test_benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows`
  - `test_benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough`
  - `test_pattern_helper_keyword_kwargs_materialize_at_callback_time`
  - `test_pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows`
  - `test_module_helper_workflow_keyword_flags_materialize_at_callback_time`
- Keep the extracted contract surface pinned to current live behavior exactly:
  - preserve the current expected-exception passthrough behavior for `benchmarks.normalize_keyword_workload_arguments(...)`, including the same accepted unexpected-keyword rows and the same unsupported-operation rejection messages;
  - preserve the current pattern-helper callback-time numeric materialization checks, including the exact `observed_field_names`, `index_calls`, `pattern.finditer` match-parity assertions, and `pattern.findall` list-result assertions;
  - preserve the current search-endpos keyword-carrier coverage exactly, including the bool and encoded-`__index__` rows and their current `assert_match_result_parity(...)` behavior; and
  - preserve the current module-helper `flags=` keyword callback-time materialization contract exactly for `module.search`, `module.match`, and `module.fullmatch`.
- Reuse the existing dedicated keyword suite instead of adding another architectural layer:
  - keep `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` as the owner for this keyword-contract surface;
  - keep using existing shared helpers such as `_record_numeric_materialization_fields`, `assert_match_result_parity`, `build_callable`, `run_benchmark_workload_with_cpython`, `workload_from_payload`, and `workload_to_payload`; and
  - do not add a new `*_support.py` module or another sibling contract suite for this extraction.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows or benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough or pattern_helper_keyword_kwargs_materialize_at_callback_time or pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows or module_helper_workflow_keyword_flags_materialize_at_callback_time'`
- `bash -lc "! rg -n 'def test_(benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows|benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough|pattern_helper_keyword_kwargs_materialize_at_callback_time|pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows|module_helper_workflow_keyword_flags_materialize_at_callback_time)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1220` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1220|RBR-1221|RBR-1222|RBR-1223" ops/state/current_status.md ops/state/backlog.md` returned no matches in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed `RBR-1218` and `RBR-1219` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `12458` lines in this run;
  - `rg -n "def test_(benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows|benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough|pattern_helper_keyword_kwargs_materialize_at_callback_time|pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows|module_helper_workflow_keyword_flags_materialize_at_callback_time)" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` currently matches only the combined-suite block at lines `11656`, `11697`, `11915`, `12112`, and `12233`;
  - `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` already exists as the dedicated owner for the adjacent module/pattern keyword contract surface; and
  - this task removes one misplaced keyword-contract block instead of creating a sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'benchmark_keyword_kwargs_normalization_preserves_expected_exception_passthrough_rows or benchmark_keyword_kwargs_normalization_does_not_expand_expected_exception_passthrough or pattern_helper_keyword_kwargs_materialize_at_callback_time or pattern_helper_keyword_kwargs_materialize_at_callback_time_for_search_endpos_rows or module_helper_workflow_keyword_flags_materialize_at_callback_time'` returned `17 passed, 145 deselected in 0.15s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those five tests still live in the combined suite.
