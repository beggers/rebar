## RBR-1356: Delete source-tree compiled-pattern contract-builder wrappers

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned compiled-pattern contract-builder wrapper functions so that the owner/spec dataclasses in `tests/benchmarks/benchmark_test_support.py` build their own `_SourceTreeContractBuilderSpec` values directly.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add owner-bound builder methods on these existing benchmark-support dataclasses:
  - `CompiledPatternModuleCompileContractCase`
  - `CompiledPatternModuleSuccessOwnerSpec`
  - `_CompiledPatternModuleHelperKeywordContractSpec`
- If those methods need shared excluded-field constants or shared note construction, keep that support in `tests/benchmarks/benchmark_test_support.py` rather than leaving source-tree-local constants behind only to serve deleted wrappers.
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume the new owner-bound methods and delete these wrapper functions entirely:
  - `compiled_pattern_module_compile_contract_builder_spec`
  - `compiled_pattern_module_success_contract_builder_spec`
  - `compiled_pattern_module_helper_keyword_contract_builder_spec`
- Update the benchmark-support and consumer suites to call the owner/spec methods directly and to treat the three wrapper names as removed from the source-tree owner surface.
- Keep the cleanup bounded to this wrapper deletion:
  - do not change workload payload semantics, benchmark manifest contents, or runtime behavior
  - do not add a new helper module, alias layer, or replacement wrapper function under another name
  - do not widen into benchmark report plumbing, README text, or tracked `ops/state/` prose

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_success_rows_measured_in_combined_manifest'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `rg -n '^    def contract_builder_spec\(' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^def (compiled_pattern_module_compile_contract_builder_spec|compiled_pattern_module_success_contract_builder_spec|compiled_pattern_module_helper_keyword_contract_builder_spec)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the wrapper layer over moving it sideways; the owner/spec objects already carry the metadata needed to build these specs.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree owner inventories, routes, and anchored expectations after the wrapper removal.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1356|RBR-1357|RBR-1358|RBR-1359|RBR-1360' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned only the historical mention inside `RBR-1355`, so no higher frontier ID in that range was reserved
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still owns three top-level wrapper functions whose bodies do nothing except assemble `_SourceTreeContractBuilderSpec(...)` from metadata already held by `CompiledPatternModuleCompileContractCase`, `CompiledPatternModuleSuccessOwnerSpec`, or `_CompiledPatternModuleHelperKeywordContractSpec`
  - those wrapper names are still referenced from `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, and `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, so deleting them cleanly requires one bounded cross-file refactor rather than another local tidy-up
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `99 passed in 1.25s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile_contract_rows_preserve_success_and_keyword_payload_round_trip_until_helper_invocation or compiled_pattern_wrong_text_model_contract_rows_preserve_source_order_and_payload_round_trip_until_helper_invocation or haystack_text_model_validation_accepts_exact_pattern_boundary_wrong_text_model_trio'` passed with `12 passed, 52 deselected in 0.20s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile_contract_rows_stay_anchored_to_published_correctness_cases or run_internal_workload_probe_measures_compiled_pattern_wrong_text_model_contract_workloads or run_internal_workload_probe_measures_compiled_pattern_module_helper_keyword_contract_workloads or compiled_pattern_module_success_rows_measured_in_combined_manifest'` passed with `53 passed, 226 deselected in 0.25s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `rg -n '^    def contract_builder_spec\(' tests/benchmarks/benchmark_test_support.py` currently fails because the owner/spec dataclasses do not yet provide those builder methods, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^def (compiled_pattern_module_compile_contract_builder_spec|compiled_pattern_module_success_contract_builder_spec|compiled_pattern_module_helper_keyword_contract_builder_spec)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those three wrapper functions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
