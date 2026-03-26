## RBR-1382: Delete collection replacement combined slice factory

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the `_collection_replacement_combined_slice_expectation(...)` factory from the collection-replacement benchmark owner layer, and express `COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS` as plain `_CollectionReplacementCombinedSliceExpectation(...)` literals instead of routing static slice data through a normalization wrapper.

## Deliverables
- `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Remove `_collection_replacement_combined_slice_expectation(...)` from `tests/benchmarks/collection_replacement_benchmark_anchor_support.py` without replacing it with another generic builder or wrapper helper.
- Rewrite every entry in `COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS` to use direct `_CollectionReplacementCombinedSliceExpectation(...)` literals while keeping the same bounded slice surface:
  - the tuple order and `slice_id` values stay unchanged;
  - each expectation keeps the same `manifest_id`, required/excluded categories, required/excluded syntax features, required row categories, `expected_status`, and `required_id_suffix`;
  - each expectation keeps the same `expected_workload_ids`, `expected_patterns`, `expected_operations`, and `expected_haystacks` values after the wrapper is removed.
- Keep `_CollectionReplacementCombinedSliceExpectation` as the concrete stored shape for the owner surface; this task is about deleting the factory layer, not replacing the dataclass with a different abstraction.
- Update `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` so the owner/test surface no longer treats the deleted factory as part of the module structure and still proves that the quantified callable slice expectations stay in sync with the owner workload-id constants.
- Do not change benchmark manifests, workload ids, benchmark execution behavior, published row ids, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '_collection_replacement_combined_slice_expectation\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"`

## Constraints
- Prefer plain dataclass literals and explicit tuple/frozenset values over another builder, registry, or coercion helper.
- Keep the run bounded to the combined-slice factory deletion in the collection-replacement benchmark-support owner layer.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1382|RBR-1383|RBR-1384' ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` returned no reserved or existing matches in this run
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - `_collection_replacement_combined_slice_expectation(...)` has one definition and nine call sites, all in `COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS`.
  - The factory does not add behavior beyond coercing already-static owner literals into tuples and frozensets before constructing `_CollectionReplacementCombinedSliceExpectation`.
  - The focused test file already isolates the live owner boundary around these expectations, including the quantified callable workload-id sync contract.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed with `152 passed in 1.66s`
  - `python3 -m py_compile tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed
  - `bash -lc "rg -n '_collection_replacement_combined_slice_expectation\\(' tests/benchmarks/collection_replacement_benchmark_anchor_support.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py"` currently fails with the exact helper definition and nine call sites this task is intended to delete
