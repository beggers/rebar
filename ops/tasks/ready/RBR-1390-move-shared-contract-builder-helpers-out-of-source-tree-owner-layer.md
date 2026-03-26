## RBR-1390: Move shared contract-builder helpers out of the source-tree owner layer

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the cross-file dependency that currently makes generic benchmark contract-builder and combined-suite import-audit helpers live under `tests/benchmarks/source_tree_benchmark_anchor_support.py`, even though unrelated benchmark support and tests call them. Rehome that shared machinery under `tests/benchmarks/benchmark_test_support.py` and leave the source-tree owner module focused on source-tree-owned expectations and selectors.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Move the generic contract-builder helpers out of `tests/benchmarks/source_tree_benchmark_anchor_support.py` and into `tests/benchmarks/benchmark_test_support.py` without replacing them with another source-tree-owned alias layer:
  - `_SourceTreeContractBuilderSpec`
  - `_source_tree_contract_manifest(...)`
  - `_source_tree_contract_workload(...)`
- Move the shared combined-suite AST/import-audit helpers out of `tests/benchmarks/source_tree_benchmark_anchor_support.py` and into `tests/benchmarks/benchmark_test_support.py` under benchmark-support ownership, then rewire their existing cross-file consumers:
  - `_parsed_source_tree_combined_suite_ast(...)`
  - `_assert_source_tree_combined_routes_owner_names_through_module_alias(...)`
- Rewrite `tests/benchmarks/benchmark_test_support.py`, `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`, `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`, and any affected source-tree combined benchmark tests so non-source-tree code no longer constructs contract manifests/workloads or import-audit assertions through `source_tree_support._...`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it treats those moved helpers as benchmark-support-owned and verifies that `tests/benchmarks/source_tree_benchmark_anchor_support.py` no longer exports them.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` limited to source-tree-owned support after the move; remove any imports that were only needed for the migrated helpers, but do not widen into unrelated support cleanup.
- Do not change workload definitions, benchmark manifests, published scorecards, benchmark execution behavior, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_contract_manifest or source_tree_contract_workload or SourceTreeContractBuilderSpec or parsed_source_tree_combined_suite_ast or assert_source_tree_combined_routes_owner_names_through_module_alias'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'source_tree_support\\._(SourceTreeContractBuilderSpec|source_tree_contract_manifest|source_tree_contract_workload|parsed_source_tree_combined_suite_ast|assert_source_tree_combined_routes_owner_names_through_module_alias)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer moving the shared helpers into the existing `tests/benchmarks/benchmark_test_support.py` layer instead of creating another owner-neutral helper module.
- Keep the run bounded to this ownership cleanup. Do not fold in unrelated source-tree expectation refactors, collection-replacement helper reductions, or broader benchmark-support naming cleanup.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1390|RBR-1391|RBR-1392|RBR-1393|RBR-1394|RBR-1395' ops/state/current_status.md ops/state/backlog.md` returned no reserved future-id hits for `RBR-1390`.
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty in this checkout, so there was no ready or blocked duplicate to refine or reopen first.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - With tracked and live JSON counts both at zero, I looked for a remaining cross-file layer rather than another local wrapper deletion.
  - `tests/benchmarks/benchmark_test_support.py` currently constructs shared compiled-pattern contract specs through `source_tree_support._SourceTreeContractBuilderSpec(...)`, and multiple non-source-tree test modules call `source_tree_support._source_tree_contract_manifest(...)`, `source_tree_support._source_tree_contract_workload(...)`, or `source_tree_support._assert_source_tree_combined_routes_owner_names_through_module_alias(...)`.
  - That leaves a source-tree owner module carrying generic benchmark-support machinery for unrelated owners, which is a real ownership leak and a better post-JSON simplification target than another single-helper deletion inside the same file.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'source_tree_contract_manifest or source_tree_contract_workload or SourceTreeContractBuilderSpec or parsed_source_tree_combined_suite_ast or assert_source_tree_combined_routes_owner_names_through_module_alias'` passed with `3 passed, 811 deselected in 0.23s`.
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `rg -n 'source_tree_support\\._(SourceTreeContractBuilderSpec|source_tree_contract_manifest|source_tree_contract_workload|parsed_source_tree_combined_suite_ast|assert_source_tree_combined_routes_owner_names_through_module_alias)\\b' tests/benchmarks/benchmark_test_support.py tests/benchmarks/test_benchmark_test_support.py tests/benchmarks/test_benchmark_manifest_validation.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently reports the exact cross-owner references this task is intended to remove.
