## RBR-1306: Delete compiled-pattern module success support wrapper

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` layer by moving its remaining direct-success owner surface onto `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, so the compiled-pattern module-helper family stops carrying a second support module plus a dedicated wrapper-preservation test file for logic that already belongs to the helper owner lane.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- delete `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- delete `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`

## Acceptance Criteria
- Move the remaining direct-success compiled-pattern module-helper support surface off `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` and onto `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, including these names:
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
  - `_assert_compiled_pattern_module_success_payload_round_trip`
  - `_assert_compiled_pattern_success_rows_measured_in_combined_manifest`
  - `include_live_compiled_pattern_module_success_workload`
  - `live_compiled_pattern_module_success_surface_ids`
- Keep the moved direct-success support behavior unchanged:
  - preserve the current collection-replacement and module-boundary source workload ids;
  - preserve the existing callback-result and callback-call derivation through `_compiled_pattern_module_helper_route`;
  - preserve the current contract payload round-trip checks, manifest measurement assertions, and live-surface selector semantics; and
  - keep the moved names owned by `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` without introducing a new broker module, forwarding alias, or compatibility wrapper.
- Update the focused benchmark tests so they import and assert the moved success-owner surface from `tests.benchmarks.compiled_pattern_module_helper_benchmark_support` instead of the deleted wrapper module:
  - move the still-useful coverage from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` onto `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` and `tests/benchmarks/test_benchmark_test_support.py`;
  - keep the compiled-pattern helper owner-boundary assertions in `tests/benchmarks/test_benchmark_test_support.py` aligned with the single-owner module shape after the delete; and
  - do not leave a replacement file whose primary purpose is preserving the deleted wrapper boundary.
- Delete `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` once nothing under `tests/benchmarks` imports it anymore.
- Delete `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` once its still-useful behavior/ownership assertions have been absorbed into the focused helper-support tests above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or compiled_pattern_module_helper or shared_compiled_pattern_helper'`
- `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_success_benchmark_support.py && test ! -e tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py && ! rg -n 'compiled_pattern_module_success_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Prefer one owner module over two. The point is to collapse the extra compiled-pattern success support layer, not to relocate it behind another compatibility alias or another file.
- Preserve the ownership split already landed in the recent `RBR-1302` through `RBR-1305` sequence: generic shared helpers stay in `tests/benchmarks/benchmark_test_support.py`, while compiled-pattern module-helper-specific support stays with `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.

## Notes
- `RBR-1306` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1306|RBR-1307|RBR-1308" ops/state/current_status.md ops/state/backlog.md` returned no live reservation for `RBR-1306`.
- No blocked architecture task existed to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` is a `278`-line support module whose only repo-local consumers are benchmark tests;
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` is a `360`-line dedicated wrapper-preservation test file for that support layer; and
  - `rg -n "compiled_pattern_module_success_benchmark_support" tests/benchmarks -g '*.py'` currently reports imports only from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` and `tests/benchmarks/test_benchmark_test_support.py`, plus the module-name string checks inside those same tests.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or compiled_pattern_module_helper or shared_compiled_pattern_helper'` passed with `116 passed, 160 deselected in 0.93s`; and
  - `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_success_benchmark_support.py && test ! -e tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py && ! rg -n 'compiled_pattern_module_success_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the wrapper module, its dedicated test file, and live imports still exist, and that failure belongs exactly to this cleanup.

## Completion Note
- Moved the compiled-pattern direct-success owner surface into `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`, preserved the existing source workload ids and helper-route callback derivation, folded the still-useful contract/selector coverage into `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`, updated `tests/benchmarks/test_benchmark_test_support.py` to assert the single helper-owner module shape, and deleted the wrapper support module plus its dedicated wrapper-preservation test file.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_success or compiled_pattern_module_helper or shared_compiled_pattern_helper'` (`113 passed, 160 deselected`) and `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_success_benchmark_support.py && test ! -e tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py && ! rg -n 'compiled_pattern_module_success_benchmark_support' tests/benchmarks -g '*.py'"`. `git diff --name-status -- tests/benchmarks/compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` now reports `D` for both deleted tracked files.
