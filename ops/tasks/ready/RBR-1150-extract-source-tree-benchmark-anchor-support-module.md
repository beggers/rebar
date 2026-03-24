# RBR-1150: Extract source-tree benchmark anchor support module

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the benchmark anchor-support library that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared support plus its synthetic contract checks into dedicated benchmark-support files, so the combined owner file stops carrying both the support implementation and the benchmark-owner assertions.

## Deliverables
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/source_tree_benchmark_anchor_support.py` for the anchor-resolution helpers that are currently defined inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `AnchoredWorkloadCasePair`, `freeze_signature_value(...)`, `published_case_ids_by_signature(...)`, `published_cases_by_id(...)`, `_manifest_workloads(...)`, `anchored_workload_case_ids(...)`, `unanchored_workload_ids(...)`, `expected_anchored_workload_case_pairs(...)`, and `assert_anchored_workload_case_result_parity(...)` onto that module;
  - keep the helper surface ordinary Python support code rather than introducing a registry, loader indirection, or another abstraction layer; and
  - preserve the current cache behavior and the current correctness-to-benchmark parity dispatch exactly.
- Add focused contract coverage at `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` by moving the current synthetic-manifest support tests out of the combined owner file:
  - cover the current nested-signature freezing behavior;
  - cover grouped published-case lookup, anchored/unanchored workload resolution, manifest-load cache reuse, and the current failure modes for manifest drift, multiple case ids, missing workloads, and unpublished cases; and
  - keep the delegated parity assertion check that proves `assert_anchored_workload_case_result_parity(...)` still routes through the expected-result helper.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the new support module instead of defining the support library inline:
  - keep the benchmark-owner integration checks in this file, including `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(...)` and `test_standard_benchmark_workload_callbacks_match_anchor_case_results(...)`;
  - remove the moved helper definitions and the moved synthetic anchor-support contract tests from this file once the new support module and support-test file fully cover them; and
  - keep any remaining file-local benchmark-owner helpers local only when they are still used exclusively by this owner file after the extraction.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'freeze_signature_value or published_case_ids_by_signature_groups_duplicate_case_ids or anchored_and_unanchored_workload_helpers_follow_signatures_and_filters or expected_anchored_workload_case_pairs_return_matching_objects or manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries or expected_anchored_workload_case_pairs_rejects_manifest_name_drift or expected_anchored_workload_case_pairs_rejects_multiple_case_ids or expected_anchored_workload_case_pairs_rejects_missing_workload or expected_anchored_workload_case_pairs_rejects_unpublished_case or assert_anchored_workload_case_result_parity_delegates_expected_values or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workload_callbacks_match_anchor_case_results'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the duplicated inline support layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over adding a wrapper module that simply re-exports the same names back into that file.
- Preserve the current helper names, cache semantics, anchored-workload selection behavior, and benchmark-versus-correctness parity expectations exactly.

## Notes
- `RBR-1150` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1150|RBR-1151|RBR-1152|RBR-1153' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical notes inside completed task files and did not reveal a live reservation at `RBR-1150`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and benchmark-side in the current checkout:
  - `tests/benchmarks/` currently contains only `test_source_tree_combined_boundary_benchmarks.py`;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `21795` lines in this run; and
  - `rg -n '^class AnchoredWorkloadCasePair$|^def (freeze_signature_value|published_case_ids_by_signature|published_cases_by_id|anchored_workload_case_ids|unanchored_workload_ids|expected_anchored_workload_case_pairs|assert_anchored_workload_case_result_parity)\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently returns the inline support definitions at lines `7167`, `7179`, `7196`, `7227`, `7248`, `7267`, and `7320`, while the synthetic helper-contract tests for that support still live near lines `21085` through `21403`.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'freeze_signature_value or published_case_ids_by_signature_groups_duplicate_case_ids or anchored_and_unanchored_workload_helpers_follow_signatures_and_filters or expected_anchored_workload_case_pairs_return_matching_objects or manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries or expected_anchored_workload_case_pairs_rejects_manifest_name_drift or expected_anchored_workload_case_pairs_rejects_multiple_case_ids or expected_anchored_workload_case_pairs_rejects_missing_workload or expected_anchored_workload_case_pairs_rejects_unpublished_case or assert_anchored_workload_case_result_parity_delegates_expected_values or standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workload_callbacks_match_anchor_case_results'` returned `83 passed, 679 deselected` in this run.
