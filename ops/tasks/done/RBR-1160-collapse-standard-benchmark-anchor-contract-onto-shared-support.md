## RBR-1160: Collapse standard benchmark anchor contract onto shared support

Status: done
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining standard-benchmark anchor contract layer that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving the shared contract dataclass and its anchor-expectation builder helpers onto `tests/benchmarks/standard_benchmark_anchor_support.py`, so the combined owner file stops carrying both the support API and the large inventory of benchmark definitions that consume it.

## Deliverables
- `tests/benchmarks/standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Extend `tests/benchmarks/standard_benchmark_anchor_support.py` so it owns the remaining generic standard-anchor contract surface that is still embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`:
  - move `StandardBenchmarkAnchorContractDefinition`;
  - move `_definition_anchor_expectations(...)`, `_workload_case_pairs_workload_ids(...)`, `_workload_case_pairs_case_ids(...)`, and `_workload_case_pair_anchor_expectations(...)`;
  - keep the module as ordinary Python support code that works with the existing standard-benchmark definitions and routes without adding a registry, loader indirection, or a new benchmark-definition abstraction; and
  - preserve the current `includes_workload(...)` filtering behavior, expected-anchor mapping shape, and tuple ordering exactly.
- Add focused coverage in `tests/benchmarks/test_standard_benchmark_anchor_support.py` for the moved support surface:
  - cover the moved contract dataclass's `includes_workload(...)` behavior across excluded and special-unanchored workload ids;
  - cover `_definition_anchor_expectations(...)` and `_workload_case_pair_anchor_expectations(...)` on lightweight synthetic manifest/workload inputs;
  - cover `_workload_case_pairs_workload_ids(...)` and `_workload_case_pairs_case_ids(...)`; and
  - keep the new tests focused on the extracted support behavior instead of copying the owner file's full integration matrix.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so it imports and uses the moved support surface instead of defining it inline:
  - remove the moved dataclass and helper definitions from this file once the shared support module owns them;
  - keep the benchmark-definition inventory, route-specific signature builders, and the standard-benchmark integration assertions in this owner file; and
  - preserve the current standard-benchmark parametrization, anchor expectations, callback parity routing, special-unanchored handling, and legacy-anchor handling exactly.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'`

## Constraints
- Keep the cleanup structural and limited to the three benchmark-support files above. Do not widen it into benchmark manifests, harness implementation code, correctness fixtures, README text, or tracked ops state prose.
- Prefer deleting the remaining inline contract/builder layer from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` over leaving wrappers there that simply forward into the support module.
- Do not change route-specific benchmark anchor logic such as collection-replacement, compile-proxy, compiled-pattern contract lanes, or manifest-shape expectations in this task.

## Notes
- `RBR-1160` is the next available unreserved architecture task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n 'RBR-1160|RBR-1161|RBR-1162|RBR-1163|RBR-1164|RBR-1165' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run.
- No blocked architecture task exists to reopen or retire first in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The remaining shared benchmark-support layer is still concrete in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still defines `StandardBenchmarkAnchorContractDefinition` plus `_definition_anchor_expectations(...)`, `_workload_case_pairs_workload_ids(...)`, `_workload_case_pairs_case_ids(...)`, and `_workload_case_pair_anchor_expectations(...)` at lines `7472` through `7523`;
  - those helpers are used broadly across the standard benchmark definition inventory and route helpers later in the same file; and
  - `tests/benchmarks/standard_benchmark_anchor_support.py` already owns the rest of the standard-anchor helper layer, so moving this contract/builder surface there is a bounded continuation rather than a new abstraction.
- Verification status in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` returned `25 passed` in this run.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'` returned `155 passed, 598 deselected` in this run.

## Completion Note
- Moved `StandardBenchmarkAnchorContractDefinition` plus `_definition_anchor_expectations(...)`, `_workload_case_pairs_workload_ids(...)`, `_workload_case_pairs_case_ids(...)`, and `_workload_case_pair_anchor_expectations(...)` into `tests/benchmarks/standard_benchmark_anchor_support.py`, updated the combined owner file to import that shared surface, and added focused synthetic coverage for the moved support behavior.
- Verification in this run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_standard_benchmark_anchor_support.py` returned `8 passed`.
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_workloads_stay_anchored_to_published_correctness_cases or standard_benchmark_workloads_stay_pinned_to_exact_case_ids or standard_benchmark_special_unanchored_workloads_stay_explicit or standard_benchmark_special_unanchored_bytes_workloads_stay_covered_by_direct_parity_cases or standard_benchmark_legacy_workloads_stay_pinned_to_expected_case_ids or standard_benchmark_workload_callbacks_match_anchor_case_results or standard_benchmark_special_unanchored_workloads_match_manual_cpython_dispatch'` returned `155 passed, 598 deselected`.
