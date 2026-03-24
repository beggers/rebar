# RBR-1183: Extract benchmark recording double support

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the duplicated benchmark callback-recording doubles that still live in multiple benchmark test files, and stop `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` from importing the giant combined suite just to reuse those private classes.

## Deliverables
- `tests/benchmarks/recording_benchmark_module_support.py`
- `tests/benchmarks/test_recording_benchmark_module_support.py`
- `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`

## Acceptance Criteria
- Add one bounded shared support module at `tests/benchmarks/recording_benchmark_module_support.py` for the benchmark callback-recording doubles that are currently copied across benchmark tests:
  - move the benchmark `compile()` recording behavior into one shared `RecordingBenchmarkModule` surface;
  - move the direct compiled-pattern helper recording behavior into one shared `RecordingBenchmarkCompiledPattern` surface; and
  - keep support for the current optional `compile_exception` and `helper_exception` injection paths plus the current recorded call tuple shapes.
- Keep that shared support pinned to the current benchmark callback contract instead of widening it:
  - preserve the existing `module.search` / `module.match` / `module.fullmatch` / `module.split` / `module.findall` / `module.finditer` / `module.sub` / `module.subn` callback return shapes;
  - preserve the existing direct `pattern.search` / `pattern.match` / `pattern.fullmatch` / `pattern.split` / `pattern.sub` / `pattern.subn` recording behavior used by the cache and wrong-text-model tests; and
  - preserve the current `compiled_patterns` list semantics and precompile-first expectations.
- Delete the duplicated local double definitions instead of leaving wrappers or aliases behind:
  - remove `class _RecordingBenchmarkCompiledPattern` and `class _RecordingBenchmarkModule` from `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`;
  - remove `class _RecordingBenchmarkCompiledPattern` and `class _RecordingBenchmarkModule` from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`; and
  - remove `class _RecordingBenchmarkCompiledPattern` and `class _RecordingBenchmarkModule` from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Update the affected tests to import the shared recording support instead of private local copies:
  - keep the compile-support precompile and exception tests on the same call-order expectations in `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`;
  - keep the compiled-pattern module-success callback tests on the same precompile-first expectations in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`;
  - keep the giant combined suite cache and compiled-pattern helper-keyword callback tests on the same expectations in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - update `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` to import the new shared support module directly instead of importing `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` as `combined`.
- Add one dedicated support test file at `tests/benchmarks/test_recording_benchmark_module_support.py` that pins the shared recording-double behavior without reintroducing another giant cross-file dependency:
  - cover one compile-only case;
  - cover one helper-exception case; and
  - cover one direct compiled-pattern helper call case.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_recording_benchmark_module_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or module_helper_cache_modes_preserve_expected_compile_and_purge_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'`

## Constraints
- Keep the cleanup structural and limited to the files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, reports, README text, or tracked ops state prose.
- Prefer one shared support module over another test-to-test import or another private local copy.
- Do not turn this into a broader refactor of unrelated benchmark helpers, anchor support, or contract-builder support.

## Notes
- `RBR-1183` is the next available unreserved architecture task id in this checkout:
  - `RBR-1182` is already reserved in `ops/state/backlog.md`; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are otherwise empty in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification is still live and cross-file in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` still defines local recording doubles at lines `82` and `86`;
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` still defines local recording doubles at lines `39` and `43`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines local recording doubles at lines `16019` and `16065`; and
  - `tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` still imports `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` as `combined` at line `19` only to reuse `combined._RecordingBenchmarkModule`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_recording_benchmark_module_support.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_recording_benchmark_module_support.py`, which belongs to the exact cleanup queued here.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` returned `78 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` returned `41 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_wrong_text_model_benchmark_owner_support.py` returned `52 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing or module_helper_cache_modes_preserve_expected_compile_and_purge_order or module_helper_warm_expected_exception_prewarms_compile_cache_without_invoking_helper or pattern_helper_cache_modes_preserve_expected_compile_and_purge_order'` returned `17 passed, 577 deselected` in this run.
