## RBR-1196: Collapse compiled-pattern benchmark validation onto dedicated suite

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining compiled-pattern manifest-validation block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated validation owner in `tests/benchmarks/test_benchmark_manifest_validation.py`, so the giant combined benchmark suite stops owning validation-only coverage that does not depend on its broader source-tree anchor wiring.

## Deliverables
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_benchmark_manifest_validation.py` so it becomes the owner for the current compiled-pattern validation-only block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated validation file without widening their scope or changing their assertions:
  - `test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points`
  - `test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows`
  - `test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points`
- Preserve the current contract surface exactly:
  - keep the current manifest-vs-payload entry-point parity assertions, error strings, manifest ids, workload ids, cache-mode constraints, kwargs payload handling, and bounded `IGNORECASE` rejection-row round-trip expectations unchanged;
  - keep the existing dependency on `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` for `COMPILED_PATTERN_MODULE_COMPILE_KEYWORD_CASE_GROUPS` and `CompiledPatternModuleCompileContractCase` instead of re-declaring those cases locally; and
  - do not introduce another `*_support.py` module, helper wrapper, or copied case table just to complete this move.
- Delete the moved block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving aliases, wrappers, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not widen it into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows or compiled_pattern_validation_matches_manifest_and_payload_entry_points'`
- `bash -lc "! rg -n 'test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows|test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1196` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1196|RBR-1197|RBR-1198|RBR-1199|RBR-1200|RBR-1201" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both the prior architecture cleanup and the current feature task through the normal done path.
- This simplification is still concrete and unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `16821` lines in this run;
  - `rg -n 'test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows|test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches lines `15961`, `16048`, and `16119`; and
  - `bash -lc "! rg -n 'test_standard_benchmark_compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows|test_standard_benchmark_compiled_pattern_validation_matches_manifest_and_payload_entry_points' tests/benchmarks/test_benchmark_manifest_validation.py"` currently succeeds, confirming the dedicated validation owner does not already contain this exact block.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py` returned `30 passed in 0.09s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows or compiled_pattern_validation_matches_manifest_and_payload_entry_points'` returned `15 passed, 551 deselected in 0.19s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the moved tests still live in the combined suite.

## Completion
- Moved the three compiled-pattern validation tests into `tests/benchmarks/test_benchmark_manifest_validation.py`, along with their tiny manifest-keyword rendering helper and the existing compiled-pattern module-compile case-group wiring derived from `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`.
- Deleted the moved tests, helper, local case-group tuple, and now-unused `CompiledPatternModuleCompileContractCase` import from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, leaving that suite free of the validation-only block.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py`, `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_validation_matches_manifest_and_payload_entry_points or compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows or compiled_pattern_validation_matches_manifest_and_payload_entry_points'`, and the negative `rg` check named in this task. The original combined-suite `-k` command now exits with `551 deselected` because those test ids no longer exist there after the move.
