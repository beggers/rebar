## RBR-1311: Delete compiled-pattern module-helper support layer

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` layer by moving its remaining compiled-pattern module-helper owner surface onto the surviving shared benchmark support path and updating the benchmark suites that still import it, so this compiled-pattern slice no longer travels through an extra support-only module after its dedicated wrapper suite has already been removed.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- delete `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`

## Acceptance Criteria
- Move the remaining compiled-pattern module-helper surface off `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` and onto `tests/benchmarks/benchmark_test_support.py`, including the currently imported owner and contract surface that the surviving benchmark suites still consume:
  - the compiled-pattern helper route runner and CPython callback executor used for `module.search`, `module.match`, `module.fullmatch`, `module.split`, `module.findall`, `module.finditer`, `module.sub`, and `module.subn`;
  - the wrong-text-model selectors, source-workload builders, contract-spec builders, and payload-round-trip assertions;
  - the compiled-pattern module-success owner specs, live-source selectors, payload-round-trip assertions, and measured-row expectations; and
  - the compiled-pattern module-helper keyword-contract definitions, source-workload params, precompile params, error-lane source workloads, and case-id keyed surface selection data.
- Update the surviving benchmark suites above so they import the moved compiled-pattern module-helper surface from `tests.benchmarks.benchmark_test_support` instead of the deleted support module, while preserving the current structural split:
  - `tests/benchmarks/test_benchmark_test_support.py` should stop asserting that `benchmark_test_support` lacks the compiled-pattern module-helper owner surface and instead assert that the moved definitions live there without replacing them with a new forwarding module;
  - `tests/benchmarks/test_benchmark_manifest_validation.py` should keep the current source-order, payload-round-trip, keyword materialization, and CPython outcome coverage for the compiled-pattern module-helper contract rows without routing through a deleted intermediate module; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` should keep the current zero-gap measurement, probe measurement, callback-precompile, callback-kwargs-materialization, and CPython-exception coverage for the compiled-pattern module-helper rows while importing the shared support surface directly.
- Delete `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` once its still-useful surface and coverage have been absorbed into the surviving files above.
- Keep the moved behavior unchanged:
  - preserve the current bounded literal, bounded wildcard, verbose-regression, wrong-text-model, keyword-success, and keyword-error rows;
  - preserve the current workload ids, case ids, manifest paths, expected callback/build-call shapes, and measured-row expectations; and
  - do not replace the deleted module with another broker, compatibility alias, or second support layer.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'`
- `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py && ! rg -n 'compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support and benchmark test layer above. Do not change workload manifests, harness runtime behavior, published scorecard logic, README text, or tracked `ops/state/` prose.
- Prefer deleting the support-only module over relocating it behind another compatibility shim. The point is to collapse the extra layer now that the dedicated wrapper suite is already gone.
- Keep the final ownership legible: the surviving compiled-pattern module-helper support should live on an existing shared benchmark support path rather than a new one-off helper file.

## Notes
- `RBR-1311` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1311|RBR-1312|RBR-1313|RBR-1314|RBR-1315" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1311`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` still exists as a `1110`-line standalone support module;
  - `rg -n 'compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'` currently reports exactly seven surviving benchmark-file references: `tests/benchmarks/benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_benchmark_test_support.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with multiple import/reference lines in the latter files; and
  - no production library or harness module outside `tests/benchmarks` depends on this support file, so the cleanup stays inside the benchmark support/test architecture lane.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'` passed with `105 passed, 328 deselected in 1.14s`;
  - `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py && ! rg -n 'compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the support module and its surviving references still exist, and that failure belongs exactly to this cleanup.

## Completion
- Moved the compiled-pattern module-helper benchmark support surface into `tests/benchmarks/benchmark_test_support.py`, updated the surviving benchmark suites to import that shared support path directly, and deleted `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` without leaving a forwarding module behind.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or non_owner_benchmark_support_modules_import_shared_source_tree_contract_helpers_from_support'` (`102 passed, 331 deselected in 1.31s`), `./.venv/bin/python -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, `git diff --name-status -- tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` (`D`), and `bash -lc "test ! -e tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py && ! rg -n 'compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'"`.
