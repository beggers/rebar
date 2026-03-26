## RBR-1403: Move the source-tree contract-builder spec into shared benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining reverse dependency from `tests/benchmarks/benchmark_test_support.py` into `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Shared benchmark support still imports the source-tree owner module inside `CompiledPatternModuleCompileContractCase.contract_builder_spec()`, `CompiledPatternModuleSuccessOwnerSpec.contract_builder_spec()`, and `_CompiledPatternModuleHelperKeywordContractSpec.contract_builder_spec()` only to construct `_SourceTreeContractBuilderSpec`.
- Move `_SourceTreeContractBuilderSpec` onto `tests/benchmarks/benchmark_test_support.py` and make the source-tree owner support consume that shared type instead of owning it locally.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Define `_SourceTreeContractBuilderSpec` in `tests/benchmarks/benchmark_test_support.py` and update the three shared-support `contract_builder_spec()` methods to construct it directly without importing `tests.benchmarks.source_tree_benchmark_anchor_support`.
- Delete the local `_SourceTreeContractBuilderSpec` definition from `tests/benchmarks/source_tree_benchmark_anchor_support.py` and update that module to consume the shared `benchmark_test_support._SourceTreeContractBuilderSpec` type in its contract-manifest helpers and local contract-spec assignments.
- Update the benchmark-support and source-tree-owner tests so they stop asserting that `_SourceTreeContractBuilderSpec` is owner-local and instead verify that the shared benchmark-support layer owns the type while source-tree owner support reuses it.
- Keep the run bounded to this contract-builder-spec ownership cleanup; do not also move the source-tree contract manifest builders, wrong-text-model spec dictionaries, compiled-pattern owner specs, or other benchmark helper layers in the same task.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder or owner_builder_methods_resolve_owner_surface_at_call_time or owner_methods_return_live_specs'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'contract_builder_spec or no_longer_keeps_contract_builder_spec_local'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile or compiled_pattern_module_success or helper_keyword_contract_rows_preserve_source_order'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or compiled_pattern_module_success or helper_keyword_contract_rows_preserve_source_order'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'source_tree_support\\._SourceTreeContractBuilderSpec|source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer consolidating ownership on the existing shared support module over adding another neutral helper module, registry, or wrapper layer.
- Do not change benchmark workload files, reports, README/status prose, or tracked project-state documents.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Blocked-task and duplicate check in this run:
  - `ops/tasks/blocked/` was empty, so there was no blocked architecture task to reopen or normalize first.
  - `rg -n 'RBR-1403|1403' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` found no reserved future-id use or ready/in-progress/blocked duplicate for `RBR-1403`.
- Candidate selection in this run:
  - With both tracked and live JSON counts at zero, I inspected the remaining benchmark-support ownership seams instead of widening into JSON work.
  - `rg -n 'source_tree_support\\._SourceTreeContractBuilderSpec|source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py` currently returns three owner-method imports in shared support, which is the remaining reverse dependency this task should remove.
  - I did not widen into a second candidate because this one removes a cross-file ownership seam shared across compile-contract, success-contract, and helper-keyword contract flows.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_test_support.py -k 'compiled_pattern_contract_builder or owner_builder_methods_resolve_owner_surface_at_call_time or owner_methods_return_live_specs'` passed with `13 passed, 167 deselected in 0.19s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'contract_builder_spec or no_longer_keeps_contract_builder_spec_local'` passed with `5 passed, 114 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_benchmark_manifest_validation.py -k 'compiled_pattern_module_compile or compiled_pattern_module_success or helper_keyword_contract_rows_preserve_source_order'` passed with `24 passed, 40 deselected in 0.15s`.
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'compiled_pattern_module_compile or compiled_pattern_module_success or helper_keyword_contract_rows_preserve_source_order'` passed with `116 passed, 163 deselected in 1.65s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "rg -n 'source_tree_support\\._SourceTreeContractBuilderSpec|source_tree_benchmark_anchor_support as source_tree_support' tests/benchmarks/benchmark_test_support.py"` currently returns the three reverse-dependency call sites in shared support, which is the exact seam this task should remove.
