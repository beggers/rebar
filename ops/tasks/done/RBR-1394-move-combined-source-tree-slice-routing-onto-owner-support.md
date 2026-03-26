## RBR-1394: Move combined source-tree slice routing onto owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining test-local cross-owner routing layer in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`, where the module still builds combined source-tree slice expectations and representative measured workload ids by splicing `source_tree_benchmark_anchor_support` together with collection-replacement owner exports through `_source_tree_combined_suite_slice_expectations(...)` and `_combined_source_tree_manifest_representative_measured_workload_ids(...)`.
- The combined source-tree suite should read that routed surface from `tests/benchmarks/source_tree_benchmark_anchor_support.py` instead of rebuilding the owner boundary inside the test file.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete `_source_tree_combined_suite_slice_expectations(...)` and `_combined_source_tree_manifest_representative_measured_workload_ids(...)` from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Make `tests/benchmarks/source_tree_benchmark_anchor_support.py` own the routed combined-suite surface that those helpers were rebuilding:
  - the combined source-tree slice expectation inventory used by the suite; and
  - the public representative measured workload ids for combined manifests, including the conditional collection-replacement rows that the combined suite currently appends in the test layer.
- Rewrite `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so the suite consumes only the source-tree owner support surface for that combined routing path instead of recomputing it locally.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so the owner-support contract checks assert the moved routing surface directly and keep the combined-suite import boundary honest.
- Do not add another detached router such as `tests/benchmarks/benchmark_test_support.py` helper glue, a new shared expectations table, or another test-local wrapper that just re-splices the same owner exports under a different name.
- Do not change benchmark manifests, workload contents, benchmark execution behavior, reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selected_combined_source_tree_manifest_slices_stay_covered or conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exports_combined_slice_owner_group or source_tree_support_module_exposes_routed_collection_owner_surface or combined_suite_imports_source_tree_support_through_owner_module_only'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `bash -lc "! rg -n '^def _source_tree_combined_suite_slice_expectations|^def _combined_source_tree_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural only. The point is to delete the remaining test-local cross-owner routing seam for the combined source-tree benchmark suite, not to reinterpret which conditional collection-replacement rows stay explicit, widen the published benchmark slice, or reshuffle unrelated collection-replacement helper assertions.
- Prefer moving the routing boundary onto `tests/benchmarks/source_tree_benchmark_anchor_support.py`, which already owns the combined source-tree benchmark surface, over inventing another neutral helper layer.

## Notes
- Completion (2026-03-26):
  - Moved the combined-suite routed slice surface into `tests/benchmarks/source_tree_benchmark_anchor_support.py` as `SOURCE_TREE_COMBINED_SUITE_SLICE_EXPECTATIONS` and made `source_tree_combined_manifest_representative_measured_workload_ids(...)` derive public representative ids from that owner export.
  - Deleted the combined suite's local `_source_tree_combined_suite_slice_expectations(...)` and `_combined_source_tree_manifest_representative_measured_workload_ids(...)` helpers, then rewired `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to read the routed surface directly from `source_tree_support`.
  - Updated `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to assert the new owner export, confirm the pure source-tree inventory still excludes the collection-owned block, and keep the combined suite from reading the collection-owned combined-slice constant directly.
  - Verification in this run:
    - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selected_combined_source_tree_manifest_slices_stay_covered or conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured'` passed with `2 passed, 277 deselected, 217 subtests passed in 4.09s`.
    - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exports_combined_slice_owner_group or source_tree_support_module_exposes_routed_collection_owner_surface or combined_suite_imports_source_tree_support_through_owner_module_only'` passed with `3 passed, 114 deselected in 0.30s`.
    - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
    - `bash -lc "! rg -n '^def _source_tree_combined_suite_slice_expectations|^def _combined_source_tree_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` passed.

- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1394|RBR-1395|RBR-1396' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1394`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - First I checked the current benchmark-support lane after `RBR-1393`; the deleted global benchmark-definition aggregate is gone, but `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still owns two cross-owner routing helpers that splice source-tree and collection-replacement owner data back together for the combined suite.
  - `rg -n '_source_tree_combined_suite_slice_expectations|_combined_source_tree_manifest_representative_measured_workload_ids|COLLECTION_REPLACEMENT_CONDITIONAL_GROUP_EXISTS_COMBINED_SLICE_EXPECTATIONS' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/collection_replacement_benchmark_anchor_support.py` showed that the local helpers are still the only place where the combined suite rebuilds that routed surface.
  - I also probed a broader Python parity-suite consolidation candidate, but the next obvious options were either much larger multi-suite merges or local follow-on cleanup inside existing suites, which is below the post-JSON bar compared with deleting this remaining cross-owner benchmark router.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'selected_combined_source_tree_manifest_slices_stay_covered or conditional_group_exists_template_bytes_manifest_promotes_minimal_replacement_rows_to_measured or zero_gap_bytes_manifest_promotions_keep_selected_rows_publicly_measured'` passed with `2 passed, 277 deselected, 217 subtests passed in 4.03s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'source_tree_support_module_exports_combined_slice_owner_group or source_tree_support_module_exposes_routed_collection_owner_surface or combined_suite_imports_source_tree_support_through_owner_module_only'` passed with `3 passed, 114 deselected in 0.16s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py` passed.
  - `bash -lc "rg -n 'collection_replacement_support\\.|_source_tree_combined_suite_slice_expectations|_combined_source_tree_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently reports the two local routing helpers plus their call sites, confirming the exact seam this task is meant to delete.
