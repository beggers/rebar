## RBR-1407: Move the pattern-boundary owner surface out of shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining pattern-boundary owner surface from `tests/benchmarks/benchmark_test_support.py` and the leaked pattern-boundary contract spec from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- The shared support module still owns `PATTERN_BOUNDARY_MANIFEST_PATH`, `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`, the pattern-boundary wrong-text-model selector/signature/runtime helpers, and `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS` even though their live consumers are the pattern-boundary owner suite plus narrow manifest-validation coverage for that same owner slice.
- Create a dedicated `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` owner module, move that pattern-boundary surface onto it, and leave `benchmark_test_support.py` with only neutral pattern builders and generic shared helpers while `source_tree_benchmark_anchor_support.py` keeps only generic source-tree contract helpers.

## Deliverables
- `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Create `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` and move the pattern-boundary owner surface onto it:
  - `PATTERN_BOUNDARY_MANIFEST_PATH`
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS`
  - `_pattern_boundary_wrong_text_model_source_workloads`
  - `_pattern_boundary_wrong_text_model_expected_callback_call`
  - `_run_cpython_pattern_boundary_wrong_text_model_workload`
  - `_pattern_boundary_wrong_text_model_correctness_case_signature`
  - `_pattern_boundary_wrong_text_model_workload_signature`
  - `_is_pattern_boundary_wrong_text_model_workload`
  - `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITION_NAMES`
  - `PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS`
- Move `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC` out of `tests/benchmarks/source_tree_benchmark_anchor_support.py` onto the new pattern-boundary owner module so source-tree support no longer carries a pattern-boundary-specific contract spec.
- Update `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so they route the moved pattern-boundary owner surface through `tests/benchmarks/pattern_boundary_benchmark_anchor_support.py` instead of `benchmark_test_support.py` or `source_tree_benchmark_anchor_support.py`.
- Update `tests/benchmarks/test_benchmark_test_support.py` so it no longer asserts that the moved pattern-boundary surface is shared-support-owned and instead verifies:
  - the new owner module is importable through `tests.benchmarks`
  - the deleted-module absence assertion for `tests.benchmarks.pattern_boundary_benchmark_anchor_support` is replaced with a positive ownership/import-boundary check
  - shared support still owns only the generic pattern helpers that the new owner module builds from
- Keep generic helpers shared unless a direct dependency forces a minimal adjustment:
  - `_module_pattern_case`
  - `freeze_signature_value(...)`
  - `selected_manifest_workloads(...)`
  - `run_benchmark_workload_with_cpython(...)`
  - `StandardBenchmarkAnchorContractDefinition`
- Do not widen into collection/replacement owner support, compiled-pattern module-helper support, workload manifests, generated reports, or tracked project-state docs in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'pattern_boundary'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'pattern_boundary_wrong_text_model'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias and pattern-boundary'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|PATTERN_BOUNDARY_MANIFEST_PATH|PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITION_NAMES|PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS)\\b' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "! rg -n '^_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` had no blocked architecture task to reopen or normalize.
  - `rg -n 'RBR-1407\\b|RBR-1408\\b|RBR-1409\\b' ops/state/backlog.md ops/state/current_status.md ops/tasks ops/state/decision_log.md` returned no reserved or duplicate `RBR-1407`.
- Candidate selection in this run:
  - The first viable post-JSON simplification is the pattern-boundary owner seam because it still spans two non-owner support modules: shared benchmark support owns the pattern-boundary selector/runtime/definition surface, while source-tree support leaks the contract spec for that same owner slice.
  - `rg -n 'PATTERN_BOUNDARY_STANDARD_BENCHMARK_DEFINITIONS|_pattern_boundary_wrong_text_model_source_workloads|_pattern_boundary_wrong_text_model_expected_callback_call|_run_cpython_pattern_boundary_wrong_text_model_workload|_pattern_boundary_wrong_text_model_correctness_case_signature|_pattern_boundary_wrong_text_model_workload_signature|_is_pattern_boundary_wrong_text_model_workload|_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_SOURCE_WORKLOAD_IDS|PATTERN_BOUNDARY_MANIFEST_PATH' tests/benchmarks` shows the owner surface still lives in `tests/benchmarks/benchmark_test_support.py`.
  - `rg -n '_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows the pattern-boundary contract spec still lives in source-tree support and is asserted there by current ownership tests.
  - `bash -lc "! rg -n 'pattern_boundary_benchmark_anchor_support' tests/benchmarks"` currently fails only because the owner module is still absent and `tests/benchmarks/test_benchmark_test_support.py` still contains the explicit deleted-module assertion; replacing that absence check is part of this cleanup.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` passed with `27 passed in 0.21s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'pattern_boundary'` passed with `4 passed, 176 deselected in 0.30s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'pattern_boundary_wrong_text_model'` passed with `3 passed, 61 deselected in 0.12s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias and pattern-boundary'` passed with `1 passed, 119 deselected in 0.13s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py` passed.
