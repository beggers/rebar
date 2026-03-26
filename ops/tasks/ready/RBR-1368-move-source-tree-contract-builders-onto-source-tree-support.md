# RBR-1368: Move source-tree contract builders onto source-tree support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining generic source-tree contract-builder surface from `tests/benchmarks/benchmark_test_support.py` so `_SourceTreeContractBuilderSpec`, `_source_tree_contract_manifest(...)`, and `_source_tree_contract_workload(...)` live on `tests/benchmarks/source_tree_benchmark_anchor_support.py`, the owner module already used for source-tree benchmark support routing.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Move `class _SourceTreeContractBuilderSpec`, `def _source_tree_contract_manifest(...)`, and `def _source_tree_contract_workload(...)` out of `tests/benchmarks/benchmark_test_support.py` and define them on `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead.
- Update the remaining direct consumers in `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so they call `source_tree_support._source_tree_contract_manifest(...)` and `source_tree_support._source_tree_contract_workload(...)`, not `benchmark_test_support._source_tree_contract_*`.
- Update the touched owner-boundary tests so the source-tree contract-builder ownership checks expect those names on `source_tree_benchmark_anchor_support.py` and no longer treat them as generic shared-support surface.
- Preserve the current manifest payload shape, workload payload round-tripping, anchor ids, timing defaults, and benchmark semantics; this is an ownership cleanup, not a workload-definition change.
- Prefer deleting the generic helper surface over leaving compatibility aliases on `tests/benchmarks/benchmark_test_support.py`.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_from_support or source_tree_contract_manifest or source_tree_contract_workload'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias or source_tree_contract_builder_consumer_guard_detects_direct_imports_and_local_aliases'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows or compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_cpython_dispatch_covers_success_and_keyword_lanes'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads or collection_replacement_pattern_wrong_text_model_callbacks_preserve_precompile_contract'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `rg -n '^class _SourceTreeContractBuilderSpec\\b|^def _source_tree_contract_manifest\\b|^def _source_tree_contract_workload\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^class _SourceTreeContractBuilderSpec\\b|^def _source_tree_contract_manifest\\b|^def _source_tree_contract_workload\\b' tests/benchmarks/benchmark_test_support.py"`
- `bash -lc "! rg -n 'benchmark_test_support\\._source_tree_contract_(manifest|workload)' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Keep the cleanup bounded to source-tree contract-builder ownership and the consumer-routing checks around it; do not widen into unrelated benchmark helper moves in the same run.
- Do not change benchmark workload documents, report generation, or correctness/benchmark expectations.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1368|RBR-1369|RBR-1370' ops/state/current_status.md ops/state/backlog.md` returned no matches, so this ID range was not reserved in tracked planning state
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/benchmark_test_support.py` still defines `_SourceTreeContractBuilderSpec`, `_source_tree_contract_manifest(...)`, and `_source_tree_contract_workload(...)`.
  - `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` still call `benchmark_test_support._source_tree_contract_*` directly.
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` already has owner-routing guards for these names, so the remaining direct calls are a bounded cleanup target rather than a new abstraction.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract_helper_suites_import_from_support or source_tree_contract_manifest or source_tree_contract_workload'` passed with `4 passed, 166 deselected in 0.43s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_contract_builder_consumers_route_owner_surface_through_package_alias or source_tree_contract_builder_consumer_guard_detects_direct_imports_and_local_aliases'` passed with `6 passed, 100 deselected in 0.57s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_validation_accepts_bounded_ignorecase_rejection_rows or compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation'` passed with `11 passed, 53 deselected in 0.30s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_cpython_dispatch_covers_success_and_keyword_lanes'` passed with `1 passed, 278 deselected in 0.25s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation or run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads or collection_replacement_pattern_wrong_text_model_callbacks_preserve_precompile_contract'` passed with `10 passed, 137 deselected in 0.22s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `rg -n '^class _SourceTreeContractBuilderSpec\\b|^def _source_tree_contract_manifest\\b|^def _source_tree_contract_workload\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py` currently fails because the owner module does not yet define the contract-builder surface, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^class _SourceTreeContractBuilderSpec\\b|^def _source_tree_contract_manifest\\b|^def _source_tree_contract_workload\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because the generic support module still defines all three names, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'benchmark_test_support\\._source_tree_contract_(manifest|workload)' tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails because those suites still reference the generic support path directly, and that failure belongs exactly to this cleanup
