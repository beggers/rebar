# RBR-1206: Move RecordingBenchmarkModule cache contract tests onto dedicated suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining `RecordingBenchmarkModule` cache-order contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated owner in `tests/benchmarks/test_recording_benchmark_module_support.py`, so the giant combined benchmark suite stops owning another helper-module-specific contract surface.

## Deliverables
- `tests/benchmarks/test_recording_benchmark_module_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_recording_benchmark_module_support.py` so it becomes the owner for the current `RecordingBenchmarkModule` cache-order contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing helpers and tests into that dedicated file without widening their scope or changing their assertions:
  - `_module_search_cache_contract_workload`
  - `_pattern_search_cache_contract_workload`
  - `test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order`
  - `test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper`
  - `test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current `cold`/`warm`/`purged` cache-mode parameterization and the exact expected `RecordingBenchmarkModule.calls` sequences;
  - preserve the current warm expected-exception assertion that prewarms the compile cache before the helper raises;
  - preserve the current module-helper versus pattern-helper timing scopes and callback return values;
  - preserve the current `build_callable(...)` path and `RecordingBenchmarkModule` owner instead of rewriting these tests around a different harness entry point.
- Reuse existing shared helpers instead of introducing another abstraction layer:
  - prefer `tests/benchmarks/benchmark_test_support.py::synthetic_workload(...)` for the moved workload construction rather than leaving file-local `workload_from_payload(...)` wrappers behind if the current shapes fit it;
  - keep using `tests/benchmarks/recording_benchmark_module_support.py` as the only helper-module owner for the fake recording module types; and
  - do not add a new `*_support.py` module just for this extraction.
- Delete the moved helper and test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not widen it into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_recording_benchmark_module_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_helper_cache_modes_preserve_expected_purge_and_warmup_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'`
- `bash -lc "! rg -n 'def _module_search_cache_contract_workload\\(|def _pattern_search_cache_contract_workload\\(|test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order|test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper|test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1206` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1206|RBR-1207|RBR-1208|RBR-1209|RBR-1210" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only a historical note inside `ops/tasks/done/RBR-1205-benchmark-conditional-group-exists-nested-callable-negative-count-bytes-workloads.md`, not a live reservation for this range.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed both `RBR-1204` and `RBR-1205` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is still concrete and unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `16030` lines in this run;
  - `rg -n 'def _module_search_cache_contract_workload\\(|def _pattern_search_cache_contract_workload\\(|test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order|test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper|test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently matches lines `15212`, `15244`, `15305`, `15322`, and `15384`; and
  - `bash -lc "! rg -n 'def _module_search_cache_contract_workload\\(|def _pattern_search_cache_contract_workload\\(|test_module_helper_cache_modes_preserve_expected_purge_and_warmup_order|test_module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper|test_pattern_helper_cache_modes_preserve_expected_compile_and_purge_order' tests/benchmarks/test_recording_benchmark_module_support.py"` currently succeeds, confirming the dedicated owner does not already contain this exact block.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_recording_benchmark_module_support.py` returned `3 passed in 0.04s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'module_helper_cache_modes_preserve_expected_purge_and_warmup_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'` returned `7 passed, 452 deselected in 0.15s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the moved helper/test block still lives in the combined suite.
