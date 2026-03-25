## RBR-1303: Restore dedicated compiled-pattern module-success benchmark support

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern module-success owner-spec and contract-support layer from `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`, so benchmark support/configuration lives in a dedicated support module again and the test file is left focused on assertions.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`

## Acceptance Criteria
- Add `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` as the single owner of the remaining compiled-pattern module-success support surface now defined in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`. Move the live support/configuration layer, including:
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_CONTRACT_EXCLUDED_FIELDS`
  - `_COMPILED_PATTERN_MODULE_COLLECTION_REPLACEMENT_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_SUCCESS_OWNER_SPEC`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`
  - `_COMPILED_PATTERN_MODULE_SUCCESS_SOURCE_WORKLOAD_PARAMS`
  - `_assert_compiled_pattern_module_success_payload_round_trip`
  - `_assert_compiled_pattern_success_rows_measured_in_combined_manifest`
- Update `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` to import and use that moved support surface directly instead of defining it locally. Keep the current behavioral coverage, parametrization order, contract-row checks, and callback precompile expectations intact.
- Move the support-ownership/import assertions for this surface onto `tests/benchmarks/test_benchmark_test_support.py`, so the dedicated compiled-pattern success suite stops asserting that the support layer is test-local and instead verifies the new support-module ownership.
- Do not leave compatibility aliases, forwarding wrappers, or duplicated implementations behind in `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py`. After the cleanup, that file should no longer define the dataclass or the two contract-support helpers listed above.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'`
- `bash -lc "! rg -n 'class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"`

## Constraints
- Keep this cleanup structural and bounded to the benchmark support/test layer above. Do not change benchmark manifests, harness runtime behavior, scorecard publication logic, README text, or tracked `ops/state/` prose.
- Do not fold this owner-specific surface into `tests/benchmarks/benchmark_test_support.py`. The target end state is a dedicated owner module for compiled-pattern module-success support, not another generic shared broker.
- Preserve the existing owner-spec source-workload ids, contract manifest ids, payload-shape expectations, measured-row assertions, and callback-routing behavior.

## Notes
- `RBR-1303` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this run;
  - `rg -n "RBR-1303|RBR-1304|RBR-1305" ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` found no live reservation for `RBR-1303`; and
  - the newest live task before this file was `ops/tasks/done/RBR-1302-move-shared-compiled-pattern-helper-broker-onto-benchmark-test-support.md`.
- No blocked architecture task existed to reopen or retire first in this run.
- JSON burn-down remains complete and current in this checkout:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Queue/runtime state was not in the rule-10 stall case for this run:
  - `.rebar/runtime/dashboard.md` reported a clean worktree, no ready tasks, no blocked tasks, and the most recent `architecture-implementation` run finished `done`; and
  - `.rebar/runtime/dashboard.md` showed no inherited-dirty or refresh/commit anomaly in the latest cycle snapshot.
- The live simplification target is concrete in the current checkout:
  - `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` still defines `CompiledPatternModuleSuccessOwnerSpec`, both owner-spec instances, `_COMPILED_PATTERN_MODULE_SUCCESS_OWNER_SPECS`, `_assert_compiled_pattern_module_success_payload_round_trip(...)`, and `_assert_compiled_pattern_success_rows_measured_in_combined_manifest(...)` locally;
  - `tests/benchmarks/test_benchmark_test_support.py` still only references the test module for this support surface rather than a dedicated owner module; and
  - `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` does not exist in the current checkout.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'` passed with `48 passed, 87 deselected in 0.82s`;
  - `bash -lc "! rg -n 'class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"` currently fails because that support surface still lives in the test module, and that failure belongs exactly to this cleanup.

## Completion
- Added `tests/benchmarks/compiled_pattern_module_success_benchmark_support.py` as the dedicated owner for the compiled-pattern module-success owner specs, source-workload params, live-surface helpers, and contract/payload assertions.
- Updated `tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py` to import that support surface directly and keep the behavioral assertions in the test suite.
- Moved the support-ownership checks onto `tests/benchmarks/test_benchmark_test_support.py`, including direct ownership assertions for the new support module and import-contract checks for the dedicated test suite.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_module_success'` (`51 passed, 87 deselected`) and `bash -lc "! rg -n 'class CompiledPatternModuleSuccessOwnerSpec|def _assert_compiled_pattern_module_success_payload_round_trip\\(|def _assert_compiled_pattern_success_rows_measured_in_combined_manifest\\(' tests/benchmarks/test_compiled_pattern_module_success_benchmark_support.py"`.
