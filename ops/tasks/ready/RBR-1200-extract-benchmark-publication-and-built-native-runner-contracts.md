# RBR-1200: Extract benchmark publication and built-native runner contracts

Status: ready
Owner: architecture-implementation
Created: 2026-03-24

## Goal
- Remove the remaining benchmark publication, selector, and built-native runner contract block that still lives inline inside `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` by moving that bounded generic harness surface into one dedicated benchmark test file, so the giant combined suite stops owning publication/runtime coverage that does not depend on its broader source-tree anchor wiring.

## Deliverables
- `tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one focused benchmark test file at `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` that becomes the owner for the current publication/runtime contract block now embedded in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Move the current publication/runtime helpers that only serve that block into the new dedicated file instead of leaving them inline in the giant combined suite:
  - `_tracked_benchmark_manifest_paths`
  - `_build_minimal_built_native_scorecard`
  - `_assert_built_native_runner_uses_optional_report_path`
  - `_assert_built_native_cli_uses_optional_report_path`
  - `_assert_built_native_mode_requires_real_built_runtime`
  - `_assert_built_native_combined_scorecard_fields`
  - `_benchmark_manifest_selector_id`
- Move these existing tests into that dedicated file without widening their scope or changing their assertions:
  - `test_default_benchmark_manifest_selector_rejects_unknown_selector`
  - `test_default_benchmark_published_full_suite_selector_covers_tracked_manifests`
  - `test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants`
  - `test_built_native_smoke_manifest_selector_keeps_membership_contract`
  - `test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error`
  - `test_declared_benchmark_manifest_selectors_match_registry_keys`
  - `test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order`
  - `test_published_benchmark_manifests_cache_clear_reloads_current_default_selector`
  - `test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids`
  - `test_built_native_smoke_runner_uses_explicit_report_paths_only`
  - `test_built_native_smoke_cli_uses_explicit_report_paths_only`
  - `test_built_native_smoke_mode_requires_real_built_runtime`
  - `test_built_native_smoke_mode_writes_built_native_report`
  - `test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable`
  - `test_run_benchmarks_rejects_smoke_only_selection_without_smoke_workloads`
  - `test_run_benchmarks_reports_built_native_provenance_when_available`
  - `test_built_native_full_runner_uses_explicit_report_paths_only`
  - `test_built_native_full_cli_uses_explicit_report_paths_only`
  - `test_built_native_full_mode_requires_real_built_runtime`
  - `test_built_native_full_mode_writes_built_native_report_with_known_gaps`
- Keep the extracted contract surface pinned to the current live behavior exactly:
  - preserve the current selector registry membership checks, published-manifest cache-clear reload assertions, tracked-manifest path ordering, and published manifest inventory uniqueness checks exactly;
  - preserve the current built-native smoke/full runner and CLI `report_path=None` versus explicit-report-path behavior exactly;
  - preserve the current missing-`maturin` provision-error path, source-tree fallback provenance, smoke-only no-smoke-workload rejection, and built-native provenance assertions exactly; and
  - preserve the current skip behavior for the built-native smoke/full execution tests when `maturin` is absent.
- Reuse existing helpers and shared support instead of introducing another abstraction layer:
  - keep using `tests/conftest.py` for selector-subset, selector-registry, published-manifest-helper, and published-manifest-inventory contracts;
  - keep using `tests/benchmarks/benchmark_test_support.py` for `_write_test_manifest`; and
  - do not add a new `*_support.py` module just for this extraction.
- Delete the moved helper and test block from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` instead of leaving wrappers, aliases, or duplicate copies behind.
- Keep this cleanup structural and bounded to the two files above; do not widen it into `python/rebar_harness/benchmarks.py`, benchmark workload manifests, correctness fixtures, reports, README text, or tracked ops/state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py`
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_loader_rejects_duplicate_ids or run_internal_workload_probe_reports_unsupported_operations_as_unavailable'`
- `bash -lc "! rg -n 'test_default_benchmark_manifest_selector_rejects_unknown_selector|test_default_benchmark_published_full_suite_selector_covers_tracked_manifests|test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants|test_built_native_smoke_manifest_selector_keeps_membership_contract|test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error|test_declared_benchmark_manifest_selectors_match_registry_keys|test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order|test_published_benchmark_manifests_cache_clear_reloads_current_default_selector|test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids|test_built_native_smoke_runner_uses_explicit_report_paths_only|test_built_native_smoke_cli_uses_explicit_report_paths_only|test_built_native_smoke_mode_requires_real_built_runtime|test_built_native_smoke_mode_writes_built_native_report|test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable|test_run_benchmarks_rejects_smoke_only_selection_without_smoke_workloads|test_run_benchmarks_reports_built_native_provenance_when_available|test_built_native_full_runner_uses_explicit_report_paths_only|test_built_native_full_cli_uses_explicit_report_paths_only|test_built_native_full_mode_requires_real_built_runtime|test_built_native_full_mode_writes_built_native_report_with_known_gaps' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Keep this cleanup structural and limited to the publication/runtime contract block above.
- Prefer one dedicated benchmark test file over another detached support module or more owner-to-owner imports.
- Do not turn this into a broader breakup of `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; this task is only the bounded publication/runtime extraction above.

## Notes
- `RBR-1200` is the next available unreserved task id in this checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty in this run; and
  - `rg -n "RBR-1200|RBR-1201|RBR-1202|RBR-1203|RBR-1204" ops/state/backlog.md ops/state/current_status.md ops/tasks -g '*.md'` matched only historical mentions inside completed task files, not a live reservation for this range in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down is complete and current in this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- Rule 10 does not block another architecture cleanup in this run:
  - `.rebar/runtime/dashboard.md` reports `ready: 0`, `in_progress: 0`, `blocked: 0`, `Dirty worktree: false`, and `Last Cycle Anomalies: none`; and
  - the last cycle completed both the prior architecture cleanup and the current feature task through the normal done path.
- This simplification is still concrete and unfinished in the current checkout:
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` is `16541` lines in this run;
  - `rg -n 'test_default_benchmark_manifest_selector_rejects_unknown_selector|test_default_benchmark_published_full_suite_selector_covers_tracked_manifests|test_shared_benchmark_manifest_selectors_resolve_published_subset_invariants|test_built_native_smoke_manifest_selector_keeps_membership_contract|test_benchmark_selector_subset_helper_keeps_benchmark_specific_missing_filename_error|test_declared_benchmark_manifest_selectors_match_registry_keys|test_default_benchmark_published_manifest_helper_is_cached_and_preserves_selector_order|test_published_benchmark_manifests_cache_clear_reloads_current_default_selector|test_default_benchmark_published_manifest_inventory_has_unique_manifest_and_workload_ids|test_built_native_smoke_runner_uses_explicit_report_paths_only|test_built_native_smoke_cli_uses_explicit_report_paths_only|test_built_native_smoke_mode_requires_real_built_runtime|test_built_native_smoke_mode_writes_built_native_report|test_run_benchmarks_falls_back_to_source_shim_when_build_tooling_is_unavailable|test_run_benchmarks_rejects_smoke_only_selection_without_smoke_workloads|test_run_benchmarks_reports_built_native_provenance_when_available|test_built_native_full_runner_uses_explicit_report_paths_only|test_built_native_full_cli_uses_explicit_report_paths_only|test_built_native_full_mode_requires_real_built_runtime|test_built_native_full_mode_writes_built_native_report_with_known_gaps' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches lines `10910`, `10915`, `10935`, `10950`, `10967`, `10985`, `10995`, `11006`, `11072`, `11081`, `11089`, `11100`, `11113`, `11144`, `11170`, `11218`, `11245`, `11253`, `11264`, and `11277`;
  - `rg -n 'def _tracked_benchmark_manifest_paths|def _build_minimal_built_native_scorecard|def _assert_built_native_runner_uses_optional_report_path|def _assert_built_native_cli_uses_optional_report_path|def _assert_built_native_mode_requires_real_built_runtime|def _assert_built_native_combined_scorecard_fields' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` still matches lines `8251`, `8255`, `8268`, `8305`, `8334`, and `8353`; and
  - `tests/benchmarks/test_benchmark_publication_runtime_contracts.py` does not exist in this checkout yet.
- Verification status in this planning run:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_benchmark_publication_runtime_contracts.py` currently fails with `ERROR: file or directory not found: tests/benchmarks/test_benchmark_publication_runtime_contracts.py`, which belongs exactly to the cleanup queued here;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'standard_benchmark_manifest_loader_rejects_duplicate_ids or run_internal_workload_probe_reports_unsupported_operations_as_unavailable'` returned `3 passed, 551 deselected in 0.18s` in this run; and
  - the negative `rg` check named above currently fails exactly on this cleanup because the moved tests still live in the combined suite.
