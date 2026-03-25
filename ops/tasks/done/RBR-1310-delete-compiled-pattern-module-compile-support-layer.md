## RBR-1310: Delete compiled-pattern `module.compile` support layer

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` layer by moving its remaining compiled-pattern `module.compile` owner surface onto the surviving shared benchmark support path and updating the benchmark suites that still import it, so this slice no longer travels through an extra support-only module after its dedicated wrapper suite has already been removed.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- delete `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`

## Acceptance Criteria
- Move the remaining compiled-pattern `module.compile` owner surface off `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` and onto the surviving shared benchmark support path in `tests/benchmarks/benchmark_test_support.py`, including the currently imported compile-contract and standard-definition surface that the benchmark suites still consume:
  - the standard-definition export and builder for the compiled-pattern `module.compile` slice;
  - the current success and keyword owner specs plus their anchored case/workload metadata;
  - the current contract-case/source-workload parameter groupings used by manifest-validation and combined-boundary coverage; and
  - the helper functions needed to keep the compile-contract signature, payload-round-trip, keyword-signature, expected-exception, and first-argument precompile checks behaviorally unchanged.
- Update the surviving benchmark suites above so they import the moved compiled-pattern `module.compile` surface from `tests.benchmarks.benchmark_test_support` instead of the deleted support module, while preserving the current structural split:
  - `tests/benchmarks/test_benchmark_test_support.py` keeps the ownership and wrapper-free assertions for the compiled-pattern `module.compile` standard-definition block, but points them at `benchmark_test_support`;
  - `tests/benchmarks/test_benchmark_manifest_validation.py` keeps the current compiled-pattern `module.compile` manifest/payload validation coverage without routing through a deleted intermediate module;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` keeps the current CPython dispatch, anchored-case metadata, zero-gap measurement, callback-time keyword materialization, probe measurement, and precompile-before-timing coverage for the compiled-pattern `module.compile` rows; and
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` stops treating the deleted module as a surviving former-owner support layer and keeps only the helper-sharing assertions that still make sense after the delete.
- Delete `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` once its still-useful surface and coverage have been absorbed into the surviving files above.
- Keep the moved behavior unchanged:
  - preserve the current bounded literal and named-group success rows plus the `flags=0`, `flags=False`, and `IGNORECASE` rejection keyword cases;
  - preserve the current workload ids, case ids, manifest path, anchored published-case coverage, and expected callback/build-call shapes; and
  - do not replace the deleted module with another broker, forwarding file, compatibility alias, or second support layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or former_owner_modules_share_source_tree_helpers_without_local_duplicates or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'`
- `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py && ! rg -n 'compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support and benchmark test layer above. Do not change workload manifests, harness runtime behavior, published scorecard logic, README text, or tracked `ops/state/` prose.
- Prefer deleting the support-only module over relocating it behind another compatibility shim. The point is to collapse the extra layer now that the dedicated wrapper suite is already gone.
- Keep the final ownership legible: the surviving compiled-pattern `module.compile` support should live on an existing shared benchmark support path rather than a new one-off helper file.

## Notes
- `RBR-1310` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1310|RBR-1311|RBR-1312|RBR-1313|RBR-1314" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1310`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` still exists as a `1112`-line standalone support module even though `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` has already been deleted;
  - `rg -n 'compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'` currently reports exactly five surviving benchmark-file references: `tests/benchmarks/benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_benchmark_test_support.py`, `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; and
  - no production library or harness module outside `tests/benchmarks` depends on this support file, so the cleanup stays inside the benchmark support/test architecture lane.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or former_owner_modules_share_source_tree_helpers_without_local_duplicates or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'` passed with `105 passed, 372 deselected in 1.81s`;
  - `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py && ! rg -n 'compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the support module and its surviving references still exist, and that failure belongs exactly to this cleanup.

## Completion
- Moved the compiled-pattern `module.compile` standard-definition export, owner specs, contract cases, anchor lanes, and helper functions into `tests/benchmarks/benchmark_test_support.py`, updated the surviving benchmark suites to import that shared support surface directly, trimmed the deleted-former-owner helper-sharing assertion in `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, and deleted `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or former_owner_modules_share_source_tree_helpers_without_local_duplicates or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'` -> `103 passed, 372 deselected in 1.90s`
  - `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py && ! rg -n 'compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'"` -> passed
  - `git diff --name-status -- tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` -> `D	tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`
