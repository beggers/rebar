## RBR-1398: Move the combined source-tree derivation helper layer onto owner support

Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Remove the remaining combined-suite-local derivation layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- The shared combined suite still owns `_combined_suite_slice_expectations()` and `_combined_manifest_representative_measured_workload_ids(...)` even though those helpers only merge owner-published slice expectations and derive representative workload ids from owner-maintained manifest expectations.
- Move that derivation surface onto `tests/benchmarks/source_tree_benchmark_anchor_support.py` so the combined suite consumes owner support directly instead of carrying another local routing layer.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`

## Acceptance Criteria
- Delete `_combined_suite_slice_expectations()` and `_combined_manifest_representative_measured_workload_ids(...)` from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Add owner-support helpers in `tests/benchmarks/source_tree_benchmark_anchor_support.py` that cover both responsibilities currently implemented by those suite-local helpers:
  - exposing the combined-suite slice expectation inventory needed by the shared suite; and
  - deriving representative measured workload ids for a combined target manifest by reusing explicit source-tree manifest expectations first and then appending the owner-published combined-slice workload ids that still need to stay visible.
- Keep conditional collection/replacement slice data owned by `tests/benchmarks/collection_replacement_benchmark_anchor_support.py`; the cleanup should consume that owner surface from source-tree support rather than re-encoding those expectations inside the combined suite.
- Update `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` so ownership assertions treat this derivation layer as source-tree-owner support, and update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` to consume the owner-support API instead of local wrappers.
- Do not widen into removing `_SourceTreeCombinedManifestExpectations`, rewriting the published manifest expectation table, or changing benchmark workloads, reports, or tracked project-state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'raw_manifest_expectations_omit_empty_measured_representative_defaults or combined_target_manifest_ids_exclude_only_definition_owned_base_manifests or source_tree_combined_slice_filters_match_expected_manifest_rows'`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'combined_suite_class_no_longer_defines_zero_gap_representative_wrappers or source_tree_support_defines_combined_route_helpers_locally or source_tree_combined_target_manifest_ids_preserve_order_and_exclusion_flags or select_source_tree_combined_slice_rows_filters_suffix_features_and_categories'`
- `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `bash -lc "! rg -n 'def _combined_suite_slice_expectations|def _combined_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep the run bounded to this shared combined-suite derivation cleanup. Do not widen into the fallback manifest-registry layer or broader source-tree scorecard plumbing.
- Prefer moving the derivation logic onto existing owner support over adding another neutral helper module or another suite-local wrapper.

## Notes
- Queue and JSON check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`.
  - `git status --short` was empty in this run, so the runtime counts were not lagging a dirty checkout.
  - `git ls-files '*.json' | wc -l` returned `0`.
  - `rg --files -g '*.json' | wc -l` returned `0`.
- ID and duplicate check in this run:
  - `rg -n 'RBR-1398' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked ops/tasks/done` returned only historical mentions inside completed task notes, with no reserved future-id hit and no ready/in-progress/blocked duplicate for `RBR-1398`.
  - No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate selection in this run:
  - I first checked whether `_SourceTreeCombinedManifestExpectations` could be flattened to a plain dict. That cleanup is not yet viable: `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... PY` showed 13 published manifest ids still rely on fallback containment (`collection-replacement-boundary`, `literal-flag-boundary`, `grouped-segment-boundary`, `literal-alternation-boundary`, `grouped-alternation-callable-replacement-boundary`, `nested-group-alternation-boundary`, `nested-group-replacement-boundary`, `nested-group-callable-replacement-boundary`, `optional-group-alternation-boundary`, and the four conditional empty-arm manifests), so removing the fallback layer now would widen beyond one bounded simplification.
  - I then checked the shared combined-suite derivation seam. `rg -n '^def _combined_|_combined_suite_slice_expectations|_combined_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` shows the suite still carries exactly those two local helpers, and they are referenced throughout the combined suite while only reassembling owner-published manifest and slice metadata.
  - That makes the derivation layer the next bounded post-JSON architecture task: it removes one remaining shared-suite routing layer without broadening into the larger fallback expectation registry.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'raw_manifest_expectations_omit_empty_measured_representative_defaults or combined_target_manifest_ids_exclude_only_definition_owned_base_manifests or source_tree_combined_slice_filters_match_expected_manifest_rows'` passed with `2 passed, 277 deselected in 0.14s`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'combined_suite_class_no_longer_defines_zero_gap_representative_wrappers or source_tree_support_defines_combined_route_helpers_locally or source_tree_combined_target_manifest_ids_preserve_order_and_exclusion_flags or select_source_tree_combined_slice_rows_filters_suffix_features_and_categories'` passed with `4 passed, 113 deselected in 0.16s`.
  - `python3 -m py_compile tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed.
  - `bash -lc "! rg -n 'def _combined_suite_slice_expectations|def _combined_manifest_representative_measured_workload_ids' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"` currently fails only because the exact suite-local helper layer this task should remove is still present.
