## RBR-1415: Delete the standalone pattern-boundary benchmark support layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the dedicated `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` layer now that the repo is already at zero tracked and live JSON blobs.
- The pattern-boundary benchmark lane is a small owner slice with only test consumers, and the current split forces extra import plumbing, owner-alias assertions, and one more benchmark-support module to keep in sync.
- Fold that owner surface into `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the benchmark harness keeps one fewer standalone owner module.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` (delete)
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Delete `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`.
- Recreate the deleted module's public owner surface on `tests/benchmarks/source_tree_benchmark_anchor_support.py` with the same behavior for the pattern-boundary lane, including:
  - `PATTERN_BOUNDARY_MANIFEST_PATH`
  - `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_EXCLUDED_FIELDS`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_pattern_boundary_wrong_text_model_source_workloads(...)`
  - `_pattern_boundary_wrong_text_model_expected_callback_call(...)`
  - `_pattern_boundary_wrong_text_model_correctness_case_signature(...)`
  - `_pattern_boundary_wrong_text_model_workload_signature(...)`
  - `_is_pattern_boundary_wrong_text_model_workload(...)`
  - the pattern-window, keyword-window, bounded-wildcard, and verbose-regression helpers/constants currently exported from the deleted owner module
- Update the scoped benchmark-owner tests so the pattern-boundary lane is asserted as source-tree-owned rather than routed through a dedicated `pattern_boundary_benchmark_anchor_support` module.
- Add or update deleted-module assertions in `tests/benchmarks/test_benchmark_test_support.py` so the removed module is required to stay absent and unimportable, following the existing deleted-support-module pattern in that file.
- Remove live imports of `tests.benchmarks.pattern_boundary_benchmark_anchor_support` from the scoped benchmark-owner tests and validation tests listed above.
- Keep genuinely shared helpers in `tests/benchmarks/benchmark_test_support.py`; this task should delete a support module, not reopen another helper-by-helper migration inside shared support.
- Do not widen into collection-replacement cleanup, benchmark manifest edits, benchmark report regeneration, README/status updates, or non-benchmark test support.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py -q`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py`
- `bash -lc '! test -e tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and identifier check in this run:
  - `ops/tasks/blocked/` only contained `.gitkeep`, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n "RBR-1415|RBR-1416|RBR-1417" ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks` found no reserved future-id use for `RBR-1415`; the only hit was the historical note inside the completed `RBR-1414` task file.
- Candidate selection in this run:
  - `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` is still a standalone owner module, but its consumers are limited to scoped benchmark-owner tests and validation tests.
  - `tests/benchmarks/test_benchmark_test_support.py` already has deleted-module guard helpers and prior deleted-support-module assertions, so deleting this module follows an established repo-local simplification pattern rather than inventing a new one.
  - I stopped after this first viable post-JSON candidate because it removes one entire benchmark-support layer instead of another local helper from the same support file.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py -q` passed with `404 passed in 1.43s`.
  - `python3 -m py_compile tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
  - `bash -lc '! test -e tests/benchmarks/pattern_boundary_benchmark_anchor_support.py'` currently fails only because the standalone support module still exists, which is the exact cleanup this task queues.
