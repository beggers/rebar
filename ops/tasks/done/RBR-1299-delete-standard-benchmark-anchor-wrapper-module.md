## RBR-1299: Delete standard benchmark anchor wrapper module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/standard_benchmark_anchor_support.py` wrapper module by moving its remaining generic standard-benchmark inventory helpers onto `tests/benchmarks/benchmark_test_support.py`, so the benchmark-support layer stops carrying a dedicated broker file plus a wrapper-preservation test file for logic that is now entirely shared support.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- delete `tests/benchmarks/standard_benchmark_anchor_support.py`
- delete `tests/benchmarks/test_standard_benchmark_anchor_support.py`

## Acceptance Criteria
- Move the generic shared standard-benchmark helper surface off `tests/benchmarks/standard_benchmark_anchor_support.py` and onto `tests/benchmarks/benchmark_test_support.py`, including these public or cross-file helper names:
  - `STANDARD_BENCHMARK_DEFINITIONS`
  - `_anchored_case_ids`
  - `_unanchored_case_ids`
  - `_manual_expected_result`
  - `_has_standard_benchmark_legacy_workloads`
  - `_runs_standard_benchmark_callback_result_parity`
  - `_has_standard_benchmark_special_unanchored_workloads`
  - `_has_standard_benchmark_special_unanchored_direct_parity_cases`
  - `_standard_benchmark_manifest_params`
  - `_standard_benchmark_definition_params`
  - `_standard_benchmark_definition_id`
  - `_standard_benchmark_special_unanchored_result_parity_params`
- Build `STANDARD_BENCHMARK_DEFINITIONS` directly in `tests/benchmarks/benchmark_test_support.py` by splicing the existing owner-owned tuples from:
  - `COMPILE_PROXY_STANDARD_BENCHMARK_DEFINITIONS`
  - `COLLECTION_REPLACEMENT_STANDARD_BENCHMARK_DEFINITIONS`
  - `MODULE_WORKFLOW_KEYWORD_STANDARD_BENCHMARK_DEFINITIONS`
  - `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`
  - `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`
  - `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`
  - `SOURCE_TREE_STANDARD_BENCHMARK_DEFINITIONS`
- Preserve behavior exactly:
  - keep the combined tuple order unchanged;
  - keep every definition object identical to the owner tuple member already published today;
  - keep the manifest-parameter and definition-parameter helpers returning the same ids and ordering they do now; and
  - keep the special-unanchored manual-CPython dispatch behavior unchanged.
- Update the remaining import sites so benchmark tests import the shared standard-benchmark inventory from `tests/benchmarks/benchmark_test_support.py` instead of the deleted wrapper module. This includes:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
  - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- Delete `tests/benchmarks/standard_benchmark_anchor_support.py` once no benchmark test imports it anymore.
- Delete `tests/benchmarks/test_standard_benchmark_anchor_support.py` and move any still-useful structural assertions onto the focused benchmark-support tests above and/or `tests/benchmarks/test_benchmark_test_support.py`. Do not keep a replacement file whose primary purpose is preserving a broker module boundary that no longer exists.
- Do not introduce another forwarding module, registry object, proxy class, or compatibility alias. The point is to remove the wrapper layer, not relocate it.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'`
- `bash -lc "test ! -e tests/benchmarks/standard_benchmark_anchor_support.py && test ! -e tests/benchmarks/test_standard_benchmark_anchor_support.py && ! rg -n 'standard_benchmark_anchor_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark-support/test layer above. Do not widen it into benchmark manifests, harness runner behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Preserve the existing owner split landed in the recent `RBR-1289` through `RBR-1298` sequence: owner-specific standard-definition tuples stay with their owner modules; only the shared combined inventory and shared helper functions move.
- Prefer ordinary direct imports from `tests/benchmarks/benchmark_test_support.py` over any new lazy export or compatibility indirection.

## Notes
- `RBR-1299` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are otherwise empty in this run;
  - the newest live task file before this change was `ops/tasks/done/RBR-1298-delete-lazy-standard-definition-owner-exports.md`; and
  - `rg -n "RBR-1299|RBR-1300|RBR-1301" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside done-task notes, not a live reservation for `RBR-1299`.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state is not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reports a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/dashboard.md` shows no inherited-dirty or commit-refresh anomaly in the latest cycle snapshot.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/standard_benchmark_anchor_support.py` is `280` lines and now consists of one combined standard-definition splice plus generic shared helper functions, not owner-specific benchmark logic;
  - `tests/benchmarks/test_standard_benchmark_anchor_support.py` is `1153` lines and exists primarily to preserve that wrapper boundary and its import wiring; and
  - `rg -n "standard_benchmark_anchor_support" -g '*.py'` currently reports only benchmark-test import sites plus the module and its dedicated test file.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'` passed with `257 passed, 139 deselected in 0.46s`;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'` passed with `15/299 tests collected (284 deselected) in 0.12s`; and
  - the negative `bash -lc "test ! -e tests/benchmarks/standard_benchmark_anchor_support.py && test ! -e tests/benchmarks/test_standard_benchmark_anchor_support.py && ! rg -n 'standard_benchmark_anchor_support' tests/benchmarks -g '*.py'"` command currently fails because the wrapper module, its dedicated test, and live imports still exist, and that failure belongs exactly to this cleanup.

## Completion
- Moved the shared combined standard-benchmark inventory and helper surface onto `tests/benchmarks/benchmark_test_support.py`, keeping the owner tuple splice order and definition-object identity unchanged.
- Rewired the focused benchmark tests to import `STANDARD_BENCHMARK_DEFINITIONS` from `tests/benchmarks/benchmark_test_support.py` and moved the still-useful shared-inventory assertions onto `tests/benchmarks/test_benchmark_test_support.py`.
- Deleted `tests/benchmarks/standard_benchmark_anchor_support.py` and `tests/benchmarks/test_standard_benchmark_anchor_support.py` after removing the last benchmark-test import of the wrapper module.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'`
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest --collect-only -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py -k 'standard or owner_definitions or standard_benchmark_definitions'`
  - `bash -lc "test ! -e tests/benchmarks/standard_benchmark_anchor_support.py && test ! -e tests/benchmarks/test_standard_benchmark_anchor_support.py && ! rg -n 'standard_benchmark_anchor_support' tests/benchmarks -g '*.py'"`
