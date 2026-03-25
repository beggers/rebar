## RBR-1275: Move compiled-pattern wrong-text-model contract support onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-25

## Goal
- Remove the remaining compiled-pattern wrong-text-model contract surface that still lives inside `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`, so the compiled-pattern module-helper benchmark layer keeps those contract specs, workload inventories, and payload-round-trip helpers in its existing owner support module instead of in a 720-line test file.

## Deliverables
- `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`
- `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`

## Acceptance Criteria
- Extend `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` so it becomes the single owner of the compiled-pattern wrong-text-model contract support surface currently defined in the test module:
  - `_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_compiled_pattern_wrong_text_model_specs(...)`
  - `_compiled_pattern_wrong_text_model_source_workloads(...)`
  - `_compiled_pattern_wrong_text_model_contract_spec(...)`
  - `_assert_wrong_text_model_payload_round_trip(...)`
- Update `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` to import and use that owner-owned surface instead of defining the wrong-text-model contract ids, spec builder, workload loader, and payload-round-trip helper locally.
- Preserve current behavior exactly:
  - keep the same collection-replacement and module-boundary wrong-text-model workload ids, ordering, contract filenames, contract manifest ids, excluded fields, timing scope, and note text;
  - keep `_compiled_pattern_wrong_text_model_specs(...)` selecting the same include-workload predicates and manifest paths as before;
  - keep `_compiled_pattern_wrong_text_model_source_workloads(...)` returning the same selected workload tuples in the same order;
  - keep `_compiled_pattern_wrong_text_model_contract_spec(...)` producing the same `_SourceTreeContractBuilderSpec` values as before; and
  - keep `_assert_wrong_text_model_payload_round_trip(...)` preserving the same compiled-pattern, timing-scope, haystack text-model, expected-exception, and replacement type assertions.
- Keep the cleanup structural and bounded to the two files above. Do not widen it into `python/rebar_harness/benchmarks.py`, workload manifests, other benchmark suites, README text, or tracked `ops/state/` prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
- `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs\\(|def _compiled_pattern_wrong_text_model_source_workloads\\(|def _compiled_pattern_wrong_text_model_contract_spec\\(|def _assert_wrong_text_model_payload_round_trip\\(|^_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=|^_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py"`

## Constraints
- Prefer consolidating onto the existing `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` owner module over creating another helper/support file. The point is to finish the ownership move, not to add a fresh abstraction layer.
- Keep imports direct. Do not leave compatibility aliases or forwarding wrappers in `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`.
- Do not change compiled-pattern helper routing, wrong-text-model workload selection, or assertion semantics in this task.

## Completion
- Moved the compiled-pattern wrong-text-model contract workload id tuples, spec builder, workload loader, contract builder, and payload round-trip assertions into `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py`.
- Updated `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` to import that support surface directly and removed the duplicate local definitions.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py`
  - `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs\\(|def _compiled_pattern_wrong_text_model_source_workloads\\(|def _compiled_pattern_wrong_text_model_contract_spec\\(|def _assert_wrong_text_model_payload_round_trip\\(|^_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=|^_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py"`

## Notes
- `RBR-1275` is the next available unreserved task id in this checkout:
  - `rg -n "RBR-1275|RBR-1276|RBR-1277|RBR-1278|RBR-1279" ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this run.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - the dashboard was generated at `2026-03-25T03:58:43+00:00`;
  - the dashboard HEAD matches the current `main` checkout at `0603c6f5e2d285c0502e3365dda414fb65886709`; and
  - the worktree is clean and not behind upstream, so the tracked count is not lagging in this run.
- The ownership split is concrete in the live checkout:
  - `tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` is `720` lines in this run and still defines the wrong-text-model source-workload id tuples, spec builder, workload loader, contract builder, and payload-round-trip helper locally;
  - `tests/benchmarks/compiled_pattern_module_helper_benchmark_support.py` is `669` lines and already owns the adjacent compiled-pattern module-helper route, runtime, and wrong-text-model selector surface that these contract helpers depend on; and
  - `bash -lc "! rg -n 'def _compiled_pattern_wrong_text_model_specs\\(|def _compiled_pattern_wrong_text_model_source_workloads\\(|def _compiled_pattern_wrong_text_model_contract_spec\\(|def _assert_wrong_text_model_payload_round_trip\\(|^_COMPILED_PATTERN_COLLECTION_REPLACEMENT_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=|^_COMPILED_PATTERN_MODULE_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS\\s*=' tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py"` currently fails because that support surface still lives in the test module, and that failure belongs to the exact cleanup queued here.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_compiled_pattern_module_helper_benchmark_support.py` passed with `47 passed`; and
  - the negative `rg` check in `Verification` currently fails for the expected reason described above.
