## RBR-1340: Delete redundant source-tree contract selector wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining test-local source-tree contract selector wrappers and duplicate contract spec constant from the benchmark suites so those files read owner-owned data directly instead of re-wrapping `tests.benchmarks.source_tree_benchmark_anchor_support` or `tests.benchmarks.benchmark_test_support`.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove these top-level local wrappers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and replace their call sites with direct owner-surface usage:
  - `_compiled_pattern_module_contract_case`
  - `_compiled_pattern_module_helper_keyword_contract_spec`
- Remove these top-level local wrappers and duplicate contract spec constant from `tests/benchmarks/test_benchmark_manifest_validation.py` and replace their call sites with direct owner-surface usage:
  - `_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `_compiled_pattern_module_helper_keyword_contract_surface`
  - `_compiled_pattern_module_helper_keyword_contract_spec`
- Route those call sites straight to the existing owner data:
  - `source_tree_support._COMPILED_PATTERN_MODULE_COMPILE_CONTRACT_CASES`
  - `source_tree_support.compiled_pattern_module_helper_keyword_contract_builder_spec(...)`
  - `source_tree_support._PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC`
  - `benchmark_test_support._COMPILED_PATTERN_MODULE_HELPER_KEYWORD_CONTRACT_SURFACES`
- Tighten `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it proves the two consumer files no longer define those wrapper/helper names locally while still importing `source_tree_benchmark_anchor_support` through the `tests.benchmarks` package alias.
- Keep the cleanup structural only:
  - do not introduce a new helper module, alias wrapper, or generic abstraction
  - do not widen into unrelated source-tree benchmark cleanup outside these selector/spec wrappers
  - do not move non-source-tree benchmark helpers out of their current owner modules

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k source_tree_contract_builder_consumers_route_owner_surface_through_package_alias`
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'`
- `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'`

## Constraints
- Prefer deleting the redundant local wrappers over adding another shared helper.
- Keep the owner boundary legible: the benchmark suites should consume owner-owned selectors/specs directly instead of recreating one-off forwarding helpers.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n "RBR-1340|RBR-1341|RBR-1342" ops/state ops/tasks || true` returned only historical mentions inside already-completed task notes; no reserved frontier entry exists in `ops/state/current_status.md` or `ops/state/backlog.md`
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n "^def (_compiled_pattern_module_contract_case|_compiled_pattern_module_helper_keyword_contract_spec)\\(" tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` reports the two remaining combined-suite wrappers
  - `rg -n "^(_PATTERN_BOUNDARY_WRONG_TEXT_MODEL_CONTRACT_SPEC =|def _compiled_pattern_module_helper_keyword_contract_surface\\(|def _compiled_pattern_module_helper_keyword_contract_spec\\()" tests/benchmarks/test_benchmark_manifest_validation.py` reports the duplicate manifest-validation selector/spec wrappers
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k source_tree_contract_builder_consumers_route_owner_surface_through_package_alias` passed with `4 passed, 86 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_helper_keyword_contract_rows_preserve_keyword_payload_types_field_names_and_bool_count_complements or standard_benchmark_compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation'` passed with `3 passed, 61 deselected in 0.16s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_helper_keyword_contract_callbacks_precompile_first_argument_before_timing'` passed with `7 passed, 272 deselected in 0.18s`
