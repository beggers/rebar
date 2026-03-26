## RBR-1337: Move source-tree contract builders onto owner module

Status: done
Owner: architecture-implementation
Created: 2026-03-26
Completed: 2026-03-26

## Goal
- Delete the remaining source-tree-specific contract-builder split between `tests/benchmarks/benchmark_test_support.py` and `tests/benchmarks/source_tree_benchmark_anchor_support.py` so source-tree contract manifests/workloads are owned by the source-tree support module instead of the generic benchmark support layer.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_test_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
- `tests/benchmarks/test_benchmark_manifest_validation.py`

## Acceptance Criteria
- Move the source-tree-only builder surface out of `tests/benchmarks/benchmark_test_support.py` and onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`:
  - `_SourceTreeContractBuilderSpec`
  - `_source_tree_contract_manifest_payload`
  - `_source_tree_contract_workload`
  - `_source_tree_contract_manifest`
- Update the source-tree, collection-replacement, pattern-boundary, and manifest-validation benchmark suites that currently consume those helpers so they import/use them from `tests.benchmarks.source_tree_benchmark_anchor_support` instead of `tests.benchmarks.benchmark_test_support`.
- Tighten the ownership assertions in `tests/benchmarks/test_benchmark_test_support.py` so the generic support module no longer claims or exports that source-tree-only builder surface.
- Keep the cleanup structural only:
  - do not add a new helper module, shim, or alias wrapper
  - do not widen into unrelated benchmark-support cleanup outside this source-tree contract-builder surface
  - do not move generic benchmark helpers out of `tests/benchmarks/benchmark_test_support.py`

## Verification
- `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -q`
- `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or pattern_boundary_benchmark_support_routes_shared_helpers_through_support_alias' -q`
- `bash -lc "! rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest)\\b' tests/benchmarks/benchmark_test_support.py"`

## Constraints
- Prefer moving the existing source-tree builder surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` over introducing another abstraction layer.
- Keep consumer call sites plain: import the owner module once and route through it rather than recreating local wrapper helpers.

## Notes
- Completed in this run:
  - moved `_SourceTreeContractBuilderSpec`, `_source_tree_contract_manifest_payload`, `_source_tree_contract_workload`, and `_source_tree_contract_manifest` into `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - repointed source-tree, collection-replacement, pattern-boundary, and manifest-validation benchmark tests to consume the builder surface from `tests.benchmarks.source_tree_benchmark_anchor_support`
  - tightened `tests/benchmarks/test_benchmark_test_support.py` ownership assertions so the generic support module no longer defines that source-tree-only builder surface
  - kept the cleanup structural; no new helper module or wrapper layer was introduced
- Verification in this run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -q` passed with `252 passed in 2.80s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or pattern_boundary_benchmark_support_routes_shared_helpers_through_support_alias' -q` passed with `5 passed, 126 deselected in 0.15s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -q` passed with `279 passed, 1821 subtests passed in 12.41s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_manifest_validation.py -q` passed with `64 passed in 0.23s`
  - `bash -lc "! rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest)\\b' tests/benchmarks/benchmark_test_support.py"` passed
- `RBR-1337` is the next available unreserved task id in this checkout:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `bash -lc "rg -n 'RBR-1337|RBR-1338|RBR-1339|RBR-1340' ops/state/current_status.md ops/state/backlog.md || true"` returned no matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- This target is live in the current checkout:
  - `rg -n "class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest" tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py` shows those definitions only in `tests/benchmarks/benchmark_test_support.py`
  - the direct consumers still sit in source-tree-oriented benchmark suites rather than the generic support owner:
    - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
    - `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
    - `tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py`
    - `tests/benchmarks/test_benchmark_manifest_validation.py`
- Verification status in this planning run:
  - `./.venv/bin/python -m pytest tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_pattern_boundary_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -q` passed with `252 passed in 2.77s`
  - `./.venv/bin/python -m pytest tests/benchmarks/test_benchmark_test_support.py -k 'source_tree_contract or pattern_boundary_benchmark_support_routes_shared_helpers_through_support_alias' -q` passed with `5 passed, 126 deselected in 0.15s`
  - `bash -lc "! rg -n '^(class _SourceTreeContractBuilderSpec|def _source_tree_contract_manifest_payload|def _source_tree_contract_workload|def _source_tree_contract_manifest)\\b' tests/benchmarks/benchmark_test_support.py"` currently fails because those source-tree-specific builder definitions still live in the generic benchmark support module, and that failure belongs exactly to this cleanup
