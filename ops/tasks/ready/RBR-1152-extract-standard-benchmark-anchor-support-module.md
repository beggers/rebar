## RBR-1152: Extract standard benchmark anchor support module

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the standard-benchmark anchor helper layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that shared support and its focused contract checks into dedicated benchmark-support files, so the combined owner file stops carrying both the support implementation and the standard-benchmark assertions that consume it.

## Deliverables
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one bounded shared benchmark-support module at `tests/benchmarks/standard_benchmark_anchor_support.py` for the standard-benchmark anchor helpers that currently live inline in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `_anchor_case_subset(...)`, `_expected_workload_ids(...)`, `_expected_anchor_case_ids_for_manifest(...)`, `_anchored_case_ids_for_manifest(...)`, `_anchored_case_ids(...)`, `_unanchored_case_ids(...)`, `_all_unanchored_case_ids(...)`, `_expected_callback_anchor_case_ids(...)`, `_expected_legacy_anchor_case_ids(...)`, and `_expected_anchored_pairs(...)` onto that module;
  - keep the helper surface ordinary Python support code that works against the current `StandardBenchmarkAnchorContractDefinition` shape without introducing a registry, loader indirection, or a new benchmark-definition abstraction; and
  - preserve the current anchored-case resolution, callback-anchor subset handling, legacy-anchor subset handling, and delegated use of `tests/benchmarks/source_tree_benchmark_anchor_support.py` exactly.
- Add focused contract coverage at `tests/benchmarks/test_standard_benchmark_anchor_support.py` for the moved helper surface:
  - cover workload-id filtering by manifest name;
  - cover callback-anchor and legacy-anchor subset selection;
  - cover anchored versus unanchored workload resolution and expected anchored-pair materialization through lightweight synthetic definitions and manifests; and
  - keep the new support tests focused on the extracted helper behavior instead of re-copying the full owner-file integration matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the new support module instead of defining that standard-benchmark helper layer inline:
  - keep the benchmark-owner integration checks in this file, including `test_standard_benchmark_workloads_stay_anchored_to_published_correctness_cases(...)`, `test_standard_benchmark_workloads_stay_pinned_to_exact_case_ids(...)`, `test_standard_benchmark_special_unanchored_workloads_stay_explicit(...)`, `test_standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids(...)`, and `test_standard_benchmark_workload_callbacks_match_anchor_case_results(...)`;
  - remove the moved helper definitions from this file once the new support module and support-test file fully cover them; and
  - leave the `StandardBenchmarkAnchorContractDefinition` data shape and the benchmark-definition inventory in the owner file unless the extraction proves they are shared beyond this owner file in the current checkout.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'`

## Constraints
- Keep the cleanup structural and limited to the three files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the duplicated inline helper layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over adding a wrapper module that simply re-exports the same names back into that file.
- Preserve the current standard-benchmark anchor expectations, expected workload ordering, anchored/unanchored filtering, callback-result parity routing, and legacy-anchor selection exactly.

## Notes
- `RBR-1152` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1152|RBR-1153|RBR-1154|RBR-1155' ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical notes inside completed task files and did not reveal a live reservation at `RBR-1152`.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining duplication is concrete and benchmark-side in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `21129` lines in this run;
  - `rg -n 'def _expected_workload_ids|def _expected_anchor_case_ids_for_manifest|def _anchored_case_ids_for_manifest|def _anchored_case_ids\\(|def _unanchored_case_ids\\(|def _all_unanchored_case_ids\\(|def _expected_callback_anchor_case_ids\\(|def _expected_legacy_anchor_case_ids\\(|def _expected_anchored_pairs\\(' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returns the inline helper block at lines `11264` through `11381`; and
  - those helpers are only consumed by the standard-benchmark owner assertions near lines `20614` through `20723`, which makes them a bounded extraction target rather than an implementation-facing refactor.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'` returned `155 passed, 597 deselected` in this run.
