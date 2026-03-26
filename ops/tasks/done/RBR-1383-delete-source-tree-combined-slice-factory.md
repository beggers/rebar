## RBR-1383: Delete source-tree combined slice factory

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the `_combined_slice_expectation(...)` factory from the shared source-tree benchmark owner layer, and express `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` as plain `SourceTreeCombinedSliceExpectation(...)` literals instead of routing static slice data through a normalization wrapper.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove `_combined_slice_expectation(...)` from `tests/benchmarks/source_tree_benchmark_anchor_support.py` without replacing it with another generic builder, registry, or coercion helper.
- Rewrite every entry in `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` to use direct `SourceTreeCombinedSliceExpectation(...)` literals while keeping the same bounded owner surface:
  - tuple order and `slice_id` values stay unchanged;
  - each expectation keeps the same `manifest_id`, required/excluded syntax features, required/excluded categories, required row categories, `expected_status`, and `required_id_suffix`;
  - each expectation keeps the same `expected_workload_ids`, `expected_patterns`, `expected_operations`, and `expected_haystacks` values after the wrapper is removed.
- Keep `SourceTreeCombinedSliceExpectation` as the concrete stored shape for the owner surface; this task is about deleting the factory layer, not replacing the dataclass with another abstraction.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the owner/test surface still proves the combined-slice contract and explicitly treats the deleted helper as absent from the module structure.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '_combined_slice_expectation\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer plain dataclass literals and explicit tuple and `frozenset(...)` values over another builder or normalization wrapper.
- Keep the run bounded to the shared combined-slice factory deletion in the source-tree benchmark owner layer.

## Notes
- Completed 2026-03-26: removed `_combined_slice_expectation(...)`, rewrote `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` as direct `SourceTreeCombinedSliceExpectation(...)` literals with explicit `frozenset(...)` fields, and added a support-module assertion that the deleted helper is absent from the local function surface.
- Verification completed 2026-03-26:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed (`107 passed in 1.22s`).
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
  - `bash -lc "! rg -n '_combined_slice_expectation\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` passed.
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
  - `rg -n 'RBR-1383|RBR-1384|combined_slice_expectation|delete-source-tree-combined-slice-factory|source_tree_combined_slice_expectation' ops/state/current_status.md ops/state/backlog.md ops/tasks` returned no ready/blocked duplicate and no reserved `RBR-1383`/`RBR-1384` ids in this run.
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - `_combined_slice_expectation(...)` appears once as a definition and 38 times as call sites, all within `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`.
  - The factory does not add owner-specific behavior beyond coercing already-static literals into tuples and `frozenset(...)` values before constructing `SourceTreeCombinedSliceExpectation`.
  - The focused owner test file already exercises the live `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` surface through dataclass instances, module-structure checks, and slice-selection contracts.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed with `107 passed in 1.12s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
  - `bash -lc "rg -n '_combined_slice_expectation\\(' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails with the exact helper definition and 38 call sites this task is intended to delete.
