# RBR-0557: Collapse parity-suite frontier assertions onto fixture support helpers

Status: ready
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Remove the repeated published-frontier and direct-bucket case-id assertion boilerplate from the core Python parity suites so `tests/python/fixture_parity_support.py` owns those comparisons instead of each suite reimplementing the same tuple/set-diff logic.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_public_surface_parity_suite.py`
- `tests/python/test_parser_matrix_parity_suite.py`
- `tests/python/test_match_behavior_parity_suite.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/python/test_literal_flag_parity_suite.py`

## Acceptance Criteria
- `tests/python/fixture_parity_support.py` grows the smallest shared helper surface needed to own these assertions:
  - add one helper that compares a bundle's published manifest case ids against a selected frontier plus optional uncovered/delegated case ids, preserving manifest order in the uncovered tuple;
  - add one helper that checks direct-test case-id buckets exactly cover a selected frontier and reports missing and unexpected ids clearly;
  - keep the helpers generic over the existing `FixtureBundle` surface; and
  - do not add another suite-specific registry, dataclass, or support module.
- The targeted parity suites stop open-coding the same frontier and bucket checks:
  - `tests/python/test_public_surface_parity_suite.py` routes both `test_public_surface_parity_suite_tracks_published_case_frontier()` and `test_public_surface_direct_test_buckets_cover_selected_frontier()` through the shared helper(s);
  - `tests/python/test_parser_matrix_parity_suite.py` routes both `test_parser_matrix_parity_suite_tracks_published_case_frontier()` and `test_parser_matrix_direct_test_buckets_cover_selected_frontier()` through the shared helper(s) while preserving `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS`;
  - `tests/python/test_match_behavior_parity_suite.py` routes both `test_match_behavior_parity_suite_tracks_published_case_frontier()` and `test_match_behavior_direct_test_bucket_covers_selected_frontier()` through the shared helper(s);
  - `tests/python/test_module_workflow_parity_suite.py` routes both `test_module_workflow_parity_suite_tracks_published_case_frontier()` and `test_module_workflow_direct_test_buckets_cover_selected_frontier()` through the shared helper(s); and
  - `tests/python/test_literal_flag_parity_suite.py` routes both `test_literal_flag_parity_suite_tracks_published_case_frontier()` and `test_literal_flag_direct_test_buckets_cover_selected_frontier()` through the shared helper(s) while preserving `LITERAL_FLAG_DELEGATED_CASE_IDS`.
- Preserve current behavior exactly:
  - no selected-case ids, uncovered/delegated case ids, manifest order, or direct bucket contents change;
  - `tests/python/test_public_surface_parity_suite.py`, `tests/python/test_match_behavior_parity_suite.py`, and `tests/python/test_module_workflow_parity_suite.py` still expect zero uncovered published case ids;
  - `tests/python/test_parser_matrix_parity_suite.py` still expects only `KNOWN_UNCOVERED_PARSER_MATRIX_CASE_IDS` outside its selected frontier;
  - `tests/python/test_literal_flag_parity_suite.py` still expects only `LITERAL_FLAG_DELEGATED_CASE_IDS` outside its selected frontier; and
  - do not change correctness fixtures, Rust code, benchmark workloads, published reports, README text, or tracked state files outside this task.
- `tests/python/test_fixture_parity_support_contract.py` adds focused direct coverage for the new helpers instead of broadening suite-local assertions:
  - one happy-path contract for ordered uncovered/delegated case ids;
  - one happy-path contract for direct bucket coverage; and
  - at least one failure-path contract that proves the helper reports either missing/unexpected bucket ids or frontier drift clearly.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_public_surface_parity_suite.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_match_behavior_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_literal_flag_parity_suite.py`
  - `rg -n "uncovered_case_ids = tuple\\(|missing_case_ids = tuple\\(|unexpected_case_ids = tuple\\(|manifest_case_ids\\(" tests/python/test_public_surface_parity_suite.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_match_behavior_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_literal_flag_parity_suite.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change fixture contents, selected case ids, delegated-case policy, backend behavior, benchmark coverage, or reporting output.
- Prefer extending `tests/python/fixture_parity_support.py` over adding another helper module or pushing more assertion logic into individual suite files.
- Do not broaden this run into the larger parity-suite inventory outside the five targeted files.

## Notes
- `RBR-0556` is already reserved in `ops/state/backlog.md` and `ops/state/current_status.md` for the next feature-owned broader-range open-ended grouped-alternation bytes parity follow-on, so `RBR-0557` is the next available architecture id.
- No blocked architecture task exists to reopen first, and rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were empty before this task was added;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, and `Last Cycle Anomalies: none`; and
  - `git status --short` is empty in the current checkout.
- JSON burn-down remains complete and aligned in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l = 0`; and
  - `rg --files -g '*.json' | wc -l = 0`.
- The duplicate parity-frontier surface is concrete in the current checkout:
  - `rg -n "uncovered_case_ids = tuple\\(|missing_case_ids = tuple\\(|unexpected_case_ids = tuple\\(|manifest_case_ids\\(" tests/python/test_public_surface_parity_suite.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_match_behavior_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_literal_flag_parity_suite.py` currently returns 17 matches across the five targeted suites; and
  - those matches are all variations of the same published-frontier and direct-bucket case-id comparison logic that `tests/python/fixture_parity_support.py` does not yet own.
- 2026-03-17 intake verification from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_public_surface_parity_suite.py tests/python/test_parser_matrix_parity_suite.py tests/python/test_match_behavior_parity_suite.py tests/python/test_module_workflow_parity_suite.py tests/python/test_literal_flag_parity_suite.py` passes (`482 passed, 29 skipped in 0.44s`).
