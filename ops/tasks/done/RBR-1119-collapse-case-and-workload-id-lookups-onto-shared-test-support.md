# RBR-1119: Collapse case and workload id lookups onto shared test support

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining owner-local case-id and workload-id lookup boilerplate from the shared fixture support and benchmark support tests by routing those maps through one shared helper on `tests/conftest.py` instead of rebuilding `{record.case_id: record}` and `{record.workload_id: record}` shapes inline.

## Deliverables
- `tests/conftest.py`
- `tests/python/test_shared_test_support_contract.py`
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`

## Acceptance Criteria
- Add one shared helper surface on `tests/conftest.py`, or a strictly smaller equivalent on that existing support path, that:
  - accepts an iterable of record-like objects plus an attribute name for the string id field;
  - returns a dictionary keyed by that id while preserving access to the original record objects;
  - rejects duplicate ids loudly instead of silently overwriting them; and
  - stays generic enough for at least `manifest_id`, `case_id`, and `workload_id` callers without adding a new helper module or abstraction tier.
- Keep `manifest_records_by_id()` on `tests/conftest.py` as a thin wrapper over that shared path, or replace it with a strictly smaller equivalent that preserves its current contract for existing manifest callers.
- Extend `tests/python/test_shared_test_support_contract.py` so the shared helper is covered with focused synthetic inputs, including:
  - a success case that returns the expected keyed mapping for unique record ids in input order; and
  - a duplicate-id rejection case that proves repeated ids fail loudly.
- `tests/python/fixture_parity_support.py` stops rebuilding the local `case_by_id` mapping inline inside `build_selected_fixture_bundle()` and uses the shared helper instead.
- `tests/python/test_fixture_parity_support_contract.py` stops rebuilding the zero-flag fixture contract lookup inline and uses the shared helper instead while preserving the current case order assertions.
- `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` stops carrying the owner-local `_published_cases_lookup()` and `_manifest_workloads_by_id()` wrappers and routes those case/workload id maps through the shared helper instead.
- Preserve current behavior after the cleanup:
  - selected fixture bundles still preserve requested case ordering;
  - duplicate case ids and duplicate workload ids still fail loudly instead of being overwritten;
  - benchmark anchor support still reuses cached manifest loads; and
  - no workload selection, case selection, benchmark expectation, or scorecard expectation changes.
- Keep the cleanup structural and limited to the five files above. Do not widen it into harness implementation code, reports, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py -k 'duplicate_fixture_case_ids or zero_flag_keyword_carrier' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_case_ids_by_signature or anchored_and_unanchored_workload_helpers or expected_anchored_workload_case_pairs or manifest_workload_cache'`
- `bash -lc "! rg -n 'case_by_id = \\{case\\.case_id: case for case in loaded_cases\\}|cases_by_id = \\{case\\.case_id: case for case in manifest\\.cases\\}|def _published_cases_lookup\\(|def _manifest_workloads_by_id\\(' tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`

## Constraints
- Reuse `tests/conftest.py` as the shared-support home; do not add a new helper module, cache layer, or generic registry.
- Keep the helper record-oriented and structural; do not add benchmark-specific or fixture-specific semantics beyond id-keyed lookup and duplicate rejection.
- Preserve the existing cache boundaries in `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py`; this task is about deleting duplicate lookup plumbing, not changing load frequency or cache invalidation behavior.

## Notes
- `RBR-1119` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1118`; and
  - `rg -n 'RBR-1119|RBR-1120|RBR-1121|RBR-1122|RBR-1123' ops/state/backlog.md ops/state/current_status.md` returned no reserved future ids in this run.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no task files in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/fixture_parity_support.py:275` still rebuilds a `case_id` keyed mapping from `loaded_cases` inside `build_selected_fixture_bundle()`;
  - `tests/python/test_fixture_parity_support_contract.py:5122` still rebuilds a `case_id` keyed mapping from `manifest.cases` for the zero-flag carrier contract;
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:6555` still carries `_published_cases_lookup()` as a local synthetic case-id map helper; and
  - `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py:9558` still carries `_manifest_workloads_by_id()` as a local workload-id map wrapper.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py -k 'duplicate_fixture_case_ids or zero_flag_keyword_carrier' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_case_ids_by_signature or anchored_and_unanchored_workload_helpers or expected_anchored_workload_case_pairs or manifest_workload_cache'` returned `8 passed, 1156 deselected` in this run.
- A broader benchmark-file verification is currently red for unrelated report-count drift, so it is intentionally excluded from this task's acceptance:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` currently fails at `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py::SourceTreeScorecardBenchmarkSuiteTest::test_published_full_suite_summary_reflects_collection_replacement_compiled_pattern_benchmarks` because the file still expects `999` workloads while the live report surface is `1003`.
- The negative `rg` verification currently fails exactly on the targeted lookup boilerplate above, so it is an acceptance check for this cleanup rather than unrelated repo drift.

## Completion
- Added `records_by_string_id()` to `tests/conftest.py` as the shared record-oriented id lookup helper, kept `manifest_records_by_id()` as a thin wrapper over it, and covered the new helper with focused unique-id and duplicate-id tests in `tests/python/test_shared_test_support_contract.py`.
- Replaced the fixture-support case-id lookups in `tests/python/fixture_parity_support.py` and `tests/python/test_fixture_parity_support_contract.py` with the shared helper while preserving requested case ordering and the existing duplicate fixture-case failure message.
- Removed the benchmark-file-local `_published_cases_lookup()` and `_manifest_workloads_by_id()` wrappers from `tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py` and routed those case/workload maps through the shared helper without changing the surrounding cache boundaries.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_shared_test_support_contract.py tests/python/test_fixture_parity_support_contract.py -k 'duplicate_fixture_case_ids or zero_flag_keyword_carrier' tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py -k 'published_case_ids_by_signature or anchored_and_unanchored_workload_helpers or expected_anchored_workload_case_pairs or manifest_workload_cache'` (`8 passed, 1158 deselected`) and `bash -lc "! rg -n 'case_by_id = \\{case\\.case_id: case for case in loaded_cases\\}|cases_by_id = \\{case\\.case_id: case for case in manifest\\.cases\\}|def _published_cases_lookup\\(|def _manifest_workloads_by_id\\(' tests/python/fixture_parity_support.py tests/python/test_fixture_parity_support_contract.py tests/benchmarks/test_source_tree_combined_boundary_benchmarks.py"`.
