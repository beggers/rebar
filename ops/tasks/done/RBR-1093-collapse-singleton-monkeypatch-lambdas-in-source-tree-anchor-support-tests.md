# RBR-1093: Collapse singleton monkeypatch lambdas in source-tree anchor support tests

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining trivial `monkeypatch.setattr(..., lambda: ...)` adapters from the source-tree anchor-support coverage in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` so those tests use named same-file helpers or a strictly smaller equivalent instead of four one-purpose anonymous wrappers.

## Deliverables
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` no longer contains any of these singleton monkeypatch lambdas:
  - `monkeypatch.setattr(support, "published_fixture_manifests", lambda: (manifest,))`
  - `monkeypatch.setattr(support, "published_cases_by_id", lambda: {"case-1": case})`
  - `monkeypatch.setattr(support, "published_cases_by_id", lambda: {})`
- Replace that wrapper layer with named same-file helpers, or a strictly smaller equivalent, while preserving the current support-helper coverage and test ownership surface intact:
  - `test_published_case_ids_by_signature_groups_duplicate_case_ids`
  - `test_expected_anchored_workload_case_pairs_return_matching_objects`
  - `test_manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries`
  - `test_expected_anchored_workload_case_pairs_rejects_manifest_name_drift`
  - `test_expected_anchored_workload_case_pairs_rejects_multiple_case_ids`
  - `test_expected_anchored_workload_case_pairs_rejects_missing_workload`
  - `test_expected_anchored_workload_case_pairs_rejects_unpublished_case`
  - `test_assert_anchored_workload_case_result_parity_delegates_expected_values`
- Keep the current semantics stable after the cleanup:
  - the published fixture manifest stub still returns exactly `(manifest,)`;
  - the published case lookup stubs still return `{"case-1": case}`, `{"case-1": SimpleNamespace(case_id="case-1")}`, `{"case-1": SimpleNamespace(case_id="case-1"), "case-2": SimpleNamespace(case_id="case-2")}`, and `{}` in the same tests that use them; and
  - the parity delegation helper still records the same `(workload, expected)` tuple for the anchored pair assertion.
- Keep the cleanup structural and file-local to `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`.
- Do not widen this task into `python/rebar_harness/benchmarks.py`, benchmark workloads, correctness fixtures, implementation code, reports, README copy, or tracked state prose.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_case_ids_by_signature_groups_duplicate_case_ids or expected_anchored_workload_case_pairs_return_matching_objects or manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries or expected_anchored_workload_case_pairs_rejects_manifest_name_drift or expected_anchored_workload_case_pairs_rejects_multiple_case_ids or expected_anchored_workload_case_pairs_rejects_missing_workload or expected_anchored_workload_case_pairs_rejects_unpublished_case or assert_anchored_workload_case_result_parity_delegates_expected_values'`
- `bash -lc "! rg -n 'monkeypatch\\.setattr\\(support, \"published_fixture_manifests\", lambda: \\(manifest,\\)\\)|monkeypatch\\.setattr\\(support, \"published_cases_by_id\", lambda: \\{\"case-1\": case\\}\\)|monkeypatch\\.setattr\\(support, \"published_cases_by_id\", lambda: \\{\\}\\)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Prefer deleting the anonymous monkeypatch-wrapper layer over introducing a helper registry, support module, or new abstraction tier.
- Keep the current test names, assertion coverage, case objects, and anchored-workload expectations intact.
- Keep the task bounded to the source-tree anchor-support tests above; do not broaden it into unrelated lambda cleanup elsewhere in the file.

## Notes
- `RBR-1093` is the next available unreserved task id in this checkout:
  - `ops/tasks/done/` currently runs through `RBR-1092`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` contain no live `RBR-1093` task file; and
  - `rg -n 'RBR-1093|RBR-1094|RBR-1095|RBR-1096|RBR-1097|RBR-1098|RBR-1099' ops/state/current_status.md ops/state/backlog.md ops/tasks -g '*.md'` returned only historical mentions in done-task notes, not a live reservation.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- JSON burn-down remains complete and current in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled task-refresh path.
- The simplification target is concrete in the live checkout:
  - `rg -n 'monkeypatch\\.setattr\\(support, \"published_fixture_manifests\", lambda: \\(manifest,\\)\\)|monkeypatch\\.setattr\\(support, \"published_cases_by_id\", lambda: \\{\"case-1\": case\\}\\)|monkeypatch\\.setattr\\(support, \"published_cases_by_id\", lambda: \\{\\}\\)' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` returned the remaining singleton wrappers at lines `20139`, `20196`, `20231`, and `20367` in this run.
- The focused verification slice is green in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_case_ids_by_signature_groups_duplicate_case_ids or expected_anchored_workload_case_pairs_return_matching_objects or manifest_workload_cache_reuses_one_load_for_repeated_anchor_queries or expected_anchored_workload_case_pairs_rejects_manifest_name_drift or expected_anchored_workload_case_pairs_rejects_multiple_case_ids or expected_anchored_workload_case_pairs_rejects_missing_workload or expected_anchored_workload_case_pairs_rejects_unpublished_case or assert_anchored_workload_case_result_parity_delegates_expected_values'` returned `8 passed, 724 deselected` in this run.

## Completion
- Replaced the targeted singleton `monkeypatch.setattr(..., lambda: ...)` wrappers in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` with file-local helpers using `partial(_single_manifest_tuple, ...)` and `_published_cases_lookup`.
- Verified the focused pytest slice still passes and confirmed the targeted singleton monkeypatch lambdas no longer appear in the file.
