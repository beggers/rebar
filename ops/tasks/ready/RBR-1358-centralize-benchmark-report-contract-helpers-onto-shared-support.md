## RBR-1358: Centralize benchmark report-contract helpers onto shared support

Status: ready
Owner: architecture-implementation
Created: 2026-03-26

## Goal
- Delete the remaining source-tree-owned benchmark report-contract helper layer so shared scorecard/manifest validation helpers live on `tests/benchmarks/benchmark_test_support.py` and the source-tree owner module stops acting as a transit surface for them.

## Deliverables
- `tests/benchmarks/benchmark_test_support.py`
- `tests/benchmarks/source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_benchmark_anchor_support.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add these shared helpers to `tests/benchmarks/benchmark_test_support.py`:
  - `_assert_benchmark_summary_consistent`
  - `_artifact_manifest_record`
  - `assert_source_tree_benchmark_contract`
  - `assert_benchmark_manifest_contract`
  - `find_manifest_record`
- Update `tests/benchmarks/source_tree_benchmark_anchor_support.py` to consume those helpers from `benchmark_test_support` and delete the local definitions entirely.
- Update the source-tree owner-surface inventories/tests so those five helper names are no longer treated as source-tree-owned or source-tree-routed surface.
- Update `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` to call the shared helpers from `benchmark_test_support` directly instead of routing them through `source_tree_support`.
- Keep the cleanup bounded to helper centralization:
  - do not change benchmark scorecard semantics, manifest selection behavior, or workload/report contents
  - do not move source-tree-specific combined-slice helpers or owner-spec data out of `tests/benchmarks/source_tree_benchmark_anchor_support.py`
  - do not add a replacement wrapper, alias shim, or new support module

## Verification
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_support_module_exposes_moved_report_contract_helpers or test_combined_suite_routes_moved_support_surfaces_through_source_tree_support or test_source_tree_support_module_imports_shared_support_through_tests_benchmarks_package_only or test_source_tree_owner_imports_shared_support_through_tests_benchmarks_package_only'`
- `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_runner_regenerates_source_tree_scorecards or test_single_manifest_benchmark_scorecards_still_cover_their_target_manifests'`
- `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`
- `rg -n '^def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/benchmark_test_support.py`
- `bash -lc "! rg -n '^def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"`
- `bash -lc "! rg -n 'source_tree_support\\.(assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"`

## Constraints
- Prefer deleting the source-tree transit layer over moving it sideways; the report-contract helpers validate shared scorecard structure rather than source-tree-owned benchmark selection logic.
- Keep `tests/benchmarks/source_tree_benchmark_anchor_support.py` focused on source-tree owner inventories, combined-slice expectations, and source-tree-specific selectors after the cleanup.

## Notes
- ID check in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, and `tracked_json_blob_count: 0`
  - `git ls-files '*.json' | wc -l` returned `0`
  - `rg --files -g '*.json' | wc -l` returned `0`
  - `rg -n 'RBR-1358|RBR-1359|RBR-1360|RBR-1361' ops/state/current_status.md ops/state/backlog.md ops/state/decision_log.md ops/tasks -g '*.md'` returned only historical mentions inside completed task notes, so no higher frontier ID in that range was reserved
- No blocked architecture task existed to reopen, refine, or normalize first in this run.
- Candidate probe that justified this task:
  - `tests/benchmarks/source_tree_benchmark_anchor_support.py` still locally defines `_assert_benchmark_summary_consistent`, `_artifact_manifest_record`, `assert_source_tree_benchmark_contract`, `assert_benchmark_manifest_contract`, and `find_manifest_record`, even though those helpers validate shared benchmark-report structure rather than source-tree-specific owner data
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still calls the public report-contract helpers through `source_tree_support` at six sites instead of importing them from shared support directly
  - `tests/benchmarks/test_source_tree_benchmark_anchor_support.py` still exercises those helper implementations through `support` and still asserts that the report-contract helper names are locally defined on the source-tree module, so deleting the transit layer requires one bounded cross-file consolidation rather than a local grep-only cleanup
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_benchmark_anchor_support.py -k 'test_source_tree_support_module_exposes_moved_report_contract_helpers or test_combined_suite_routes_moved_support_surfaces_through_source_tree_support or test_source_tree_support_module_imports_shared_support_through_tests_benchmarks_package_only or test_source_tree_owner_imports_shared_support_through_tests_benchmarks_package_only'` passed with `11 passed, 94 deselected in 0.89s`
  - `PYTHONPATH=python:. ./.venv/bin/pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'test_runner_regenerates_source_tree_scorecards or test_single_manifest_benchmark_scorecards_still_cover_their_target_manifests'` passed with `1 passed, 278 deselected, 444 subtests passed in 1.82s`
  - `python3 -m py_compile tests/benchmarks/benchmark_test_support.py tests/benchmarks/source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` passed
  - `rg -n '^def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/benchmark_test_support.py` currently fails because the shared support module does not yet define those helpers, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n '^def (_assert_benchmark_summary_consistent|_artifact_manifest_record|assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/source_tree_benchmark_anchor_support.py"` currently fails because those five helper definitions still live on the source-tree owner module, and that failure belongs exactly to this cleanup
  - `bash -lc "! rg -n 'source_tree_support\\.(assert_source_tree_benchmark_contract|assert_benchmark_manifest_contract|find_manifest_record)\\b' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py tests/benchmarks/test_source_tree_benchmark_anchor_support.py"` currently fails because both benchmark suites still route the public report-contract helpers through `source_tree_support`, and that failure belongs exactly to this cleanup
