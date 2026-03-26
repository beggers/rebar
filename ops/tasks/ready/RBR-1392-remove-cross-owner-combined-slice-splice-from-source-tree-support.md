## RBR-1392: Remove the cross-owner combined-slice splice from source-tree benchmark support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining cross-owner aggregation path where `tests/benchmarks/source_tree_benchmark_anchor_support.py` imports collection-replacement support only to splice `COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS` into `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`. The combined benchmark suite already imports both owner modules directly, so the source-tree owner should stop acting as a routed collection-owner container.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`

## Acceptance Criteria
- Stop splicing `collection_replacement_support.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS` into `tests/benchmarks/source_tree_benchmark_anchor_support.py`. After the cleanup, the source-tree owner should expose only source-tree-owned combined-slice expectations instead of a merged cross-owner inventory.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so any combined-suite inventory that still needs both owners is assembled or iterated at the suite layer from the two owner modules directly, without re-routing collection-owned slice expectations through `source_tree_support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS` or another replacement alias layer under `tests/benchmarks/`.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it no longer asserts that the collection-owned conditional replacement block is spliced into `support.SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, and instead verifies the tighter owner boundary.
- Keep the collection-replacement owner surface intact in `tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`; the cleanup should remove the routed source-tree aggregation path, not rehome the collection-owned expectation block.
- Do not change workload definitions, workload ids, manifest contents, benchmark execution behavior, generated reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_keeps_collection_routed_names_off_source_tree_module or source_tree_support_module_exposes_routed_collection_owner_surface'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_collection_replacement_combined_slice_owner_surface_uses_dataclass_literals'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n '\\*collection_replacement_support\\.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS|source_tree_combined_slice_expectations_splice_collection_owned_conditional_replacement_block_once' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the routed splice outright over replacing it with another benchmark-support-owned merged constant or another owner-neutral wrapper.
- Keep the run bounded to this owner-boundary cleanup. Do not widen into unrelated source-tree manifest expectation rewrites, collection-replacement signature changes, or broader benchmark-support refactors.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1392|RBR-1393|RBR-1394' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked` returned no matches, so there was no reserved future-id hit or duplicate ready/in-progress/blocked task for `RBR-1392`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - First I checked whether the source-tree contract-builder helpers in `tests/benchmarks/benchmark_test_support.py` had become owner-local again, but current call sites still span `test_benchmark_manifest_validation.py`, `test_collection_replacement_benchmark_anchor_support.py`, `test_pattern_boundary_benchmark_anchor_support.py`, `test_source_tree_benchmark_anchor_support.py`, and `test_source_tree_combined_boundary_benchmarks.py`, so reversing `RBR-1390` would churn ownership rather than simplify it.
  - I then checked the combined-slice routing path and found one remaining cross-owner splice: `tests/benchmarks/source_tree_benchmark_anchor_support.py` still appends `collection_replacement_support.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS` into `SOURCE_TREE_COMBINED_SLICE_EXPECTATIONS`, even though `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` already imports both owner modules directly.
  - That leaves the source-tree owner exporting a merged inventory that partially belongs to the collection-replacement owner, which is a clearer cross-file boundary leak than another one-off local helper deletion.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_owner_keeps_collection_routed_names_off_source_tree_module or source_tree_support_module_exposes_routed_collection_owner_surface'` passed with `2 passed, 114 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py -k 'quantified_conditional_callable_combined_slice_expectations_stay_in_sync_with_owner_workload_ids or conditional_collection_replacement_combined_slice_owner_surface_uses_dataclass_literals'` passed with `2 passed, 153 deselected in 0.25s`.
  - `bash -lc 'rg -n "\\*collection_replacement_support\\.COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS|source_tree_combined_slice_expectations_splice_collection_owned_conditional_replacement_block_once" tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py'` currently reports the exact routed splice and splice-specific assertion this task is intended to delete.
