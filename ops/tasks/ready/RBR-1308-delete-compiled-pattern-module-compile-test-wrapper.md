## RBR-1308: Delete compiled-pattern module.compile test wrapper

Status: ready
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Delete the standalone `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` layer by moving its still-useful compiled-pattern `module.compile` coverage onto the surviving owner suites that already exercise the same support surface, so the benchmark harness stops carrying a dedicated wrapper-preservation test file for behavior that belongs with the combined boundary, manifest-validation, and shared support checks.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- delete `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py`

## Acceptance Criteria
- Move the still-useful coverage off `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` and onto the surviving suites above, including the current assertions for:
  - success and keyword payload round-trip behavior for bounded compiled-pattern `module.compile` contract rows;
  - CPython dispatch, anchored case metadata, and zero-gap module-boundary measurement expectations for the compiled-pattern `module.compile` owner specs;
  - standard-definition export and owner-surface checks for `COMPILED_PATTERN_MODULE_COMPILE_STANDARD_BENCHMARK_DEFINITIONS`;
  - contract-row anchoring to published correctness cases, callback-time keyword materialization, internal probe measurement, and first-argument precompile behavior for compiled-pattern `module.compile` workloads; and
  - the shared-source-tree helper import/ownership assertions that currently mention the dedicated wrapper suite.
- Keep the moved coverage behavior unchanged:
  - preserve the current bounded literal/named-group success rows, keyword-signature handling, and `IGNORECASE` rejection expectations;
  - keep the surviving tests importing the owner support surface directly from `tests.benchmarks.compiled_pattern_module_compile_benchmark_support` plus the genuinely shared helpers from `tests.benchmarks.benchmark_test_support`, without introducing a new broker module, compatibility shim, or replacement wrapper file; and
  - keep the compiled-pattern `module.compile` support owned by `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` rather than relocating that support surface into a second helper layer.
- Update `tests/benchmarks/test_benchmark_test_support.py` so its ownership/import assertions match the post-delete shape:
  - stop naming `tests.benchmarks.test_compiled_pattern_module_compile_benchmark_support` as one of the dedicated source-tree helper suites;
  - keep the compiled-pattern `module.compile` owner-block and shared-helper assertions pointed at the surviving owner support module; and
  - add or retain a direct assertion that the deleted test module is no longer importable or referenced under `tests/benchmarks`.
- Delete `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` once its still-useful behavior and ownership checks have been absorbed into the surviving suites above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or source_tree_contract_helper_suites_import_from_support or standard_benchmark_definitions'`
- `bash -lc "test ! -e tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py && ! rg -n 'test_compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Prefer the surviving owner suites over a dedicated wrapper-preservation suite. The point is to delete the extra test-layer boundary, not to replace it with a new forwarding file or another compatibility alias.
- Preserve the current ownership split: `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py` remains the owner support module for this slice, while `tests/benchmarks/test_benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` absorb the focused assertions that still matter after the delete.

## Notes
- `RBR-1308` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run; and
  - `rg -n "RBR-1308|RBR-1309|RBR-1310|RBR-1311|RBR-1312" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` matched only historical mentions inside older done-task notes, not a live reservation for `RBR-1308`.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - the latest runtime snapshot showed no inherited-dirty, refresh, or commit anomaly.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py` is a `535`-line dedicated test file for a support surface whose owner module already remains at `tests/benchmarks/compiled_pattern_module_compile_benchmark_support.py`;
  - `rg -n 'test_compiled_pattern_module_compile_benchmark_support|compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'` currently reports the support-module imports that should stay plus the dedicated test file itself, with the only separate reference to the test-module name living in `tests/benchmarks/test_benchmark_test_support.py`; and
  - the three surviving target suites already cover adjacent ownership and validation boundaries for this slice, so the dedicated wrapper file is structurally redundant once its assertions are redistributed.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py -k 'compiled_pattern_module_compile or source_tree_contract_helper_suites_import_from_support or standard_benchmark_definitions'` passed with `110 passed, 205 deselected in 1.77s`, which is the current fuller baseline before the delete;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or source_tree_contract_helper_suites_import_from_support or standard_benchmark_definitions'` passed with `27 passed, 205 deselected in 0.24s`, which is the command intended to stay green after the delete; and
  - `bash -lc "test ! -e tests/benchmarks/test_compiled_pattern_module_compile_benchmark_support.py && ! rg -n 'test_compiled_pattern_module_compile_benchmark_support' tests/benchmarks -g '*.py'"` currently fails because the dedicated test file and its remaining reference still exist, and that failure belongs exactly to this cleanup.
