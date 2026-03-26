## RBR-1355: Move generic benchmark contract builders onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree ownership of the generic benchmark contract-manifest/workload builder so shared benchmark support lives in `tests/benchmarks/benchmark_test_support.py` instead of on `tests/benchmarks/source_tree_benchmark_anchor_support.py`.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Move these generic contract-builder names onto `tests/benchmarks/benchmark_test_support.py`:
  - `_SourceTreeContractBuilderSpec`
  - `_source_tree_contract_manifest`
  - `_source_tree_contract_workload`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume the shared builder instead of owning or re-exporting it.
- Update the benchmark-support and owner-surface tests so those three names are treated as shared support rather than source-tree owner surface.
- Update the non-owner benchmark suites that currently call `source_tree_support._source_tree_contract_manifest(...)` or `source_tree_support._source_tree_contract_workload(...)` to call the shared support module directly.
- Keep the cleanup bounded to this shared contract-builder relocation:
  - do not change workload payload semantics, runtime behavior, or benchmark manifest contents
  - do not add a new helper module, wrapper shim, or alias layer
  - do not widen into source-tree scorecard expectations, benchmark reports, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'test_source_tree_contract_manifest_workload_payload_drops_fields_and_injects_metadata or test_source_tree_contract_workload_reconstructs_contract_workload_with_defaults or test_source_tree_contract_manifest_uses_manifest_defaults_and_contract_ids'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'test_standard_benchmark_manifest_preserves_pattern_boundary_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_pattern_boundary_wrong_text_model_contract_workloads or test_standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^(_SourceTreeContractBuilderSpec|_source_tree_contract_manifest|_source_tree_contract_workload)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer moving the shared builder into the existing benchmark support module over adding another helper file.
- Keep the source-tree owner module focused on source-tree-specific contracts and inventories after the move.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1355|RBR-1356|RBR-1357|RBR-1358|RBR-1359|RBR-1360' ops/state/current_status.md ops/state/backlog.md` returned no matches, so no higher frontier ID in that range was reserved
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` all still call the generic contract builder through `source_tree_support`
  - the builder logic itself is generic payload-shaping code, not source-tree-specific scorecard or owner-surface logic
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'test_source_tree_contract_manifest_workload_payload_drops_fields_and_injects_metadata or test_source_tree_contract_workload_reconstructs_contract_workload_with_defaults or test_source_tree_contract_manifest_uses_manifest_defaults_and_contract_ids'` passed with `3 passed, 152 deselected in 0.24s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'test_standard_benchmark_compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or test_standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or test_standard_benchmark_haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `12 passed, 52 deselected in 0.20s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or test_run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or test_run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads'` passed with `53 passed, 226 deselected in 0.27s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'test_standard_benchmark_manifest_preserves_pattern_boundary_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_pattern_boundary_wrong_text_model_contract_workloads or test_standard_benchmark_manifest_preserves_collection_replacement_pattern_wrong_text_model_rows_until_helper_invocation or test_run_internal_workload_probe_measures_collection_replacement_pattern_wrong_text_model_contract_workloads'` passed with `14 passed, 161 deselected in 0.21s`
  - `bash -lc "! rg -n '^(_SourceTreeContractBuilderSpec|_source_tree_contract_manifest|_source_tree_contract_workload)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those three generic builder names still live on the source-tree owner module, and that failure belongs exactly to this cleanup
