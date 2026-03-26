## RBR-1395: Delete the source-tree combined-suite routing shim

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining cross-owner routing layer in `tests/benchmarks/source_tree_benchmark_anchor_support.py`, where the source-tree owner still imports `collection_replacement_benchmark_anchor_support` only to publish `SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS` and `source_tree_combined_manifest_representative_measured_workload_ids(...)` for the combined source-tree suite.
- That routed surface is now combined-suite-only. The only non-test consumer is `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, which already imports both owner modules directly, so the cross-owner combined inventory should live with that suite instead of under the source-tree owner module.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete `SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Delete `source_tree_combined_manifest_representative_measured_workload_ids(...)` from `tests/benchmarks/source_tree_benchmark_anchor_support.py`.
- Remove the `collection_replacement_benchmark_anchor_support` import from `tests/benchmarks/source_tree_benchmark_anchor_support.py`; after this cleanup, that owner module should expose only source-tree-owned combined-slice data.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it assembles any needed combined-suite cross-owner slice inventory and representative measured workload ids locally from the two owner modules it already imports, without recreating another routed export under `tests/benchmarks/benchmark_test_support.py` or a new helper module.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so it stops treating the combined-suite routed surface as source-tree-owned and instead verifies the tighter owner boundary.
- Do not change workload definitions, workload ids, benchmark execution behavior, generated reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_routed_collection_owner_surface or source_tree_support_module_exports_combined_slice_owner_group or source_tree_combined_slice_expectations_keep_collection_owned_block_out_of_source_tree_owner_inventory'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selected_combined_source_tree_manifest_slices_stay_covered or zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured or conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py`
- `bash -lc "! rg -n 'SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS|source_tree_combined_manifest_representative_measured_workload_ids|collection_support\\.' tests/benchmarks/source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the routed source-tree export layer outright over moving it to another shared helper.
- Keep the run bounded to this cross-owner routing cleanup. Do not widen into broader compiled-pattern contract refactors, owner-definition inventory changes, or benchmark manifest rewrites.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1395|RBR-1396|RBR-1397' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1395`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - First I probed the compiled-pattern contract-owner surface in `tests/benchmarks/benchmark_test_support.py`, but the live references still span `tests/benchmarks/test_benchmark_manifest_validation.py`, `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`, so deleting that family would be a wider multi-suite rearchitecture rather than one bounded cleanup.
  - I then checked the remaining cross-owner import inside `tests/benchmarks/source_tree_benchmark_anchor_support.py`. `rg -n 'SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS|source_tree_combined_manifest_representative_measured_workload_ids|collection_support\\.' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` shows that the source-tree owner still publishes one combined-suite-only routed surface, and the actual consumers are the combined suite plus source-tree owner tests.
  - That makes the routed source-tree export layer a clearer post-JSON simplification target than another helper-level trim inside the same benchmark support subsystem.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exposes_routed_collection_owner_surface or source_tree_support_module_exports_combined_slice_owner_group or source_tree_combined_slice_expectations_keep_collection_owned_block_out_of_source_tree_owner_inventory'` passed with `3 passed, 114 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selected_combined_source_tree_manifest_slices_stay_covered or zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured or conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured'` passed with `2 passed, 277 deselected, 217 subtests passed in 4.00s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_collection_replacement_benchmark_anchor_support.py` passed.
  - `bash -lc "rg -n 'SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS|source_tree_combined_manifest_representative_measured_workload_ids|collection_support\\.' tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently reports the exact routed export seam this task is intended to delete.
