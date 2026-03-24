Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the duplicate source-tree-combined slice expectation layer that still lives inside `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the dedicated runtime-contract suite stops carrying its own mini copy of the slice-selection machinery already owned by `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`

## Acceptance Criteria
- Delete the local duplicate slice-selection layer from `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`:
  - remove the local `_SourceTreeCombinedSliceExpectation` dataclass; and
  - remove the local `source_tree_combined_slice_expectations()` helper.
- Keep `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` as a direct runtime-contract owner rather than a second slice-definition owner:
  - rebuild `_nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads()` from a direct live-manifest selection local to the runtime-contract suite instead of routing through the removed expectation helper; and
  - do not import the giant combined suite, do not add a new `*_support.py` helper, and do not recreate the deleted abstraction under another name.
- Preserve the exact current nested-group callable replacement bytes slice and its assertion surface:
  - keep the workload selection pinned to these four live workload ids from `nested_group_callable_replacement_boundary.py`:
    - `module-sub-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-lower-bound-b-branch-warm-bytes`
    - `module-subn-callable-numbered-quantified-nested-group-alternation-branch-local-backreference-b-branch-first-match-only-warm-bytes`
    - `pattern-sub-callable-named-quantified-nested-group-alternation-branch-local-backreference-mixed-branches-purged-bytes`
    - `pattern-subn-callable-named-quantified-nested-group-alternation-branch-local-backreference-c-branch-first-match-only-purged-bytes`
  - keep the existing round-trip callback-result contract unchanged for those rows, including `bytes` text-model preservation plus parity between the source workload and the payload-round-tripped workload.
- Keep this cleanup bounded to the runtime-contract suite; do not change `python/rebar_harness/benchmarks.py`, workload manifests, reports, README text, ops state files, or the giant combined source-tree suite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py -k 'nested_group_callable_replacement_quantified_branch_local_backreference_bytes_workloads_round_trip_preserves_callback_results'`
- `bash -lc "! rg -n '^class _SourceTreeCombinedSliceExpectation|^def source_tree_combined_slice_expectations\\(' tests/benchmarks/test_benchmark_publication_runtime_contracts.py"`

## Notes
- Verified before queuing on 2026-03-24 that the targeted runtime-contract test currently passes in the live checkout and that the duplicate helper/class are still present in `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, so the acceptance commands isolate this cleanup rather than unrelated drift.
