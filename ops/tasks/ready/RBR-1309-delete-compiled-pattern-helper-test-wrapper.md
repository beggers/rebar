## RBR-1309: Delete compiled-pattern helper test wrapper

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` layer by moving its still-useful compiled-pattern helper coverage onto the surviving owner suites that already exercise the same support surface, so the benchmark harness stops carrying a dedicated wrapper-preservation test file for behavior that belongs with shared support, manifest validation, and combined boundary checks.

## Deliverables
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- delete `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`

## Acceptance Criteria
- Move the still-useful coverage off `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` and onto the surviving suites above, including the current assertions for:
  - owner-surface and standard-inventory checks for `COMPILED_PATTERN_MODULE_HELPER_STANDARD_BENCHMARK_DEFINITIONS`, the compiled-pattern helper support module, and its direct success and wrong-text-model selectors/signatures;
  - live-source ordering, callback/runtime contract, helper-invocation preservation, internal-probe measurement, and precompile-before-timing checks for the compiled-pattern helper wrong-text-model rows;
  - live-source selection, zero-gap measurement, internal-probe measurement, and precompile-before-timing checks for the compiled-pattern helper success owner specs; and
  - keyword-contract ownership, source ordering, round-trip payload behavior, callback-time materialization, CPython outcome parity, complement coverage, internal-probe measurement, and precompile-before-timing checks for the compiled-pattern helper collection-replacement keyword rows.
- Keep the moved coverage behavior unchanged:
  - preserve the current literal, bounded-wildcard, verbose-bytes, wrong-text-model, and keyword contract slices without changing manifest ids, workload ids, or expected callback/build-call shapes;
  - keep the surviving tests importing the owner support surface directly from `tests.benchmarks.compiled_pattern_module_helper_benchmark_support` plus the genuinely shared helpers from `tests.benchmarks.benchmark_test_support`, without introducing a new broker module, compatibility shim, or replacement wrapper file; and
  - keep ownership of the compiled-pattern helper support surface in `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` rather than pushing that support into another helper layer.
- Update `tests/benchmarks/test_benchmark_test_support.py` so its ownership/import assertions match the post-delete shape:
  - stop naming `tests.benchmarks.test_compiled_pattern_module_helper_benchmark_support` as one of the dedicated source-tree helper suites;
  - keep the shared-helper import assertions pointed at the surviving owner support module and the combined boundary suite; and
  - add or retain a direct assertion that the deleted test module is no longer importable or referenced under `tests/benchmarks`.
- Delete `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` once its still-useful behavior and ownership checks have been absorbed into the surviving suites above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or source_tree_contract_helper_suites_import_from_support or standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions or pattern_boundary_wrong_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or source_tree_contract_helper_suites_import_from_support or standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions or pattern_boundary_wrong_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `bash -lc "test ! -e tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py && ! rg -n 'test_compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Prefer the surviving owner suites over a dedicated wrapper-preservation suite. The point is to delete the extra test-layer boundary, not to replace it with a new forwarding file or another compatibility alias.
- Preserve the current ownership split: `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` remains the owner support module for this slice, while `tests/benchmarks/test_benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the focused assertions that still matter after the delete.

## Notes
- `RBR-1309` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1309|RBR-1310|RBR-1311|RBR-1312|RBR-1313" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1309`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` is a `1364`-line dedicated test file for a support surface whose owner module already remains at `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`;
  - `tests/benchmarks/test_benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already import the owner support module or adjacent shared helpers for this slice; and
  - `rg -n 'test_compiled_pattern_module_helper_benchmark_support|compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'` shows the support-module imports that should stay plus the dedicated wrapper file itself, with the only remaining test-module-name references living in `tests/benchmarks/test_benchmark_test_support.py`.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or source_tree_contract_helper_suites_import_from_support or standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions or pattern_boundary_wrong_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `203 passed, 287 deselected in 1.19s`, which is the current fuller baseline before the delete;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_helper or source_tree_contract_helper_suites_import_from_support or standard_inventory_reuses_owner_owned_compiled_pattern_module_helper_definitions or pattern_boundary_wrong_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `19 passed, 287 deselected in 0.22s`, which is the command intended to stay green after the delete; and
  - `bash -lc "test ! -e tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py && ! rg -n 'test_compiled_pattern_module_helper_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the dedicated test file and its remaining references still exist, and that failure belongs exactly to this cleanup.
