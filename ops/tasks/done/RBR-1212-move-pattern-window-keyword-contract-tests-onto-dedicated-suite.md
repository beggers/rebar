# RBR-1212: Move pattern-window keyword contract tests onto dedicated suite

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining pattern-window keyword contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving it onto the existing dedicated owner in `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`, so the giant combined benchmark suite stops owning another generic keyword-descriptor contract surface.

## Deliverables
- `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` so it becomes the owner for the current pattern-window keyword contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move these existing tests into that dedicated file without widening their scope or changing their assertion surfaces:
  - `test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation`
  - `test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points`
  - `test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current manifest payloads, workload ids, bool-versus-int checks, indexlike materialization checks, `keyword_arguments()` assertions, and stdlib outcome comparisons;
  - preserve the current validation parity between `load_manifest(...)` and `workload_from_payload(...)` for invalid keyword-carrier payloads;
  - preserve the current pytest parametrization ids and test names apart from relocating them; and
  - keep using ordinary `load_manifest(...)`, `workload_from_payload(...)`, and `run_benchmark_workload_with_cpython(...)` calls rather than inventing a new test-only representation.
- Reuse the existing dedicated suite instead of adding another architectural layer:
  - keep `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` as the owner for these pattern-window keyword contracts;
  - do not add a new `*_support.py` module or another one-off contract suite for this extraction; and
  - do not widen this cleanup into collection-replacement keyword contracts, compiled-pattern helper keyword contracts, manifest-validation tests, or benchmark harness implementation code.
- Delete the moved tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not change `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation or standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation'`
- `bash -lc "! rg -n 'test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation|test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Notes
- `RBR-1212` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run before this task was added; and
  - `rg -n "RBR-1212|RBR-1213|RBR-1214|RBR-1215|RBR-1216" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the most recent cycle completed `RBR-1210` and `RBR-1211` through the normal done path with no inherited-dirty or refresh/commit anomaly recorded.
- This simplification is concrete and still unfinished in the current checkout:
  - `rg -n 'test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation|test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` currently matches only the combined-suite block at lines `11307`, `11642`, and `11795`;
  - `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` already exists as the dedicated owner for module/pattern keyword benchmark support; and
  - this task removes one misplaced contract block instead of creating a sibling suite.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` returned `4 passed in 0.05s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation or standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation'` returned `7 passed, 440 deselected in 0.16s`; and
  - the negative `rg` check named above currently fails exactly on this cleanup because those three tests still live in the combined suite.

## Completion
- Moved the three pattern-window keyword contract tests into `tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py`, keeping the same manifest payloads, workload ids, bool-vs-int checks, indexlike materialization checks, `keyword_arguments()` assertions, validation parity, and stdlib outcome comparisons.
- Deleted the relocated tests from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the combined benchmark suite no longer owns that generic pattern-window keyword contract surface.
- Verification passed:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_module_pattern_keyword_benchmark_anchor_support.py` returned `11 passed in 0.11s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation or standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points or standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation'` now returns `440 deselected in 0.35s` with pytest exit code `5` because those tests no longer exist in the combined suite after the move.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned `440 passed, 2632 subtests passed in 40.77s`.
  - `bash -lc "! rg -n 'test_standard_benchmark_manifest_preserves_pattern_window_indexlike_descriptors_until_helper_invocation|test_standard_benchmark_keyword_kwargs_validation_matches_manifest_and_payload_entry_points|test_standard_benchmark_manifest_preserves_pattern_keyword_window_descriptors_until_helper_invocation' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` succeeded.
