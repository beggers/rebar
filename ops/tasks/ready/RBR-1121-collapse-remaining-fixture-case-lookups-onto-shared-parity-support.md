# RBR-1121: Collapse remaining fixture case lookups onto shared parity support

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining owner-local fixture `case_id` lookup maps from the Python parity suites by routing them through one shared helper on `tests/python/fixture_parity_support.py` instead of rebuilding `{case.case_id: case}` shapes inside each suite.

## Deliverables
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_parity_suite.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`

## Acceptance Criteria
- Add one shared helper surface on `tests/python/fixture_parity_support.py`, or a strictly smaller equivalent on that existing support path, that:
  - accepts either loaded fixture bundles or fixture cases from the current published-bundle flow;
  - returns a dictionary keyed by `case_id` while preserving access to the original `FixtureCase` objects;
  - rejects duplicate case ids loudly instead of silently overwriting them; and
  - stays fixture-oriented rather than introducing a new generic registry layer or helper module.
- Extend `tests/python/test_fixture_parity_support_contract.py` so the shared helper is covered with focused synthetic inputs, including:
  - a success case that returns the expected keyed mapping for unique case ids in input order; and
  - a duplicate-id rejection case that proves repeated case ids fail loudly.
- `tests/python/test_grouped_capture_parity_suite.py`, `tests/python/test_branch_local_backreference_parity_suite.py`, and `tests/python/test_conditional_group_exists_parity_suite.py` stop rebuilding `CASES_BY_ID` from local `_iter_fixture_cases()` generators and use the shared helper instead.
- `tests/python/test_literal_flag_parity_suite.py` stops rebuilding `LITERAL_FLAG_CASES_BY_ID` inline and uses the shared helper instead.
- `tests/python/test_quantified_alternation_parity_suite.py` stops rebuilding `COMPILE_CASES_BY_ID` inline and uses the shared helper instead.
- Preserve current behavior after the cleanup:
  - published bundle loading order remains unchanged;
  - compile, module, pattern, and direct-bytes follow-on assertions keep selecting the same case rows as before;
  - duplicate case ids still fail loudly instead of being overwritten; and
  - no fixture selection, parity expectation, or backend-behavior changes.
- Keep the cleanup structural and limited to the seven files above. Do not widen it into harness implementation code, reports, README text, or tracked project-state prose.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundles_by_manifest_id or load_single_published_fixture_bundle' tests/python/test_grouped_capture_parity_suite.py::test_match_group_access_rows_remain_on_grouped_capture_fixture_paths tests/python/test_branch_local_backreference_parity_suite.py::test_pattern_bounds_cases_stay_anchored_to_supported_backreference_patterns tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_literal_flag_parity_suite.py::test_literal_ignorecase_module_helpers_match_cpython tests/python/test_quantified_alternation_parity_suite.py::test_compile_metadata_matches_cpython`
- `bash -lc "! rg -n 'CASES_BY_ID = \\{case\\.case_id: case for case in _iter_fixture_cases\\(\\)\\}|LITERAL_FLAG_CASES_BY_ID = \\{|COMPILE_CASES_BY_ID = \\{' tests/python/test_grouped_capture_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_conditional_group_exists_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py"`

## Constraints
- Reuse `tests/python/fixture_parity_support.py` as the shared-support home; do not add a new helper module, cache layer, or abstraction tier.
- Keep the helper case-oriented and structural; do not add suite-specific semantics beyond keyed lookup and duplicate rejection.
- Preserve current bundle/case ordering and existing parity-suite fixture boundaries; this task is about deleting duplicate lookup plumbing, not changing which published rows each suite covers.

## Notes
- `RBR-1121` is the next available unreserved task id in this checkout:
  - the highest live task id across `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, and `ops/tasks/blocked/` is `1120`; and
  - `rg -n 'RBR-1121|RBR-1122|RBR-1123|RBR-1124|RBR-1125' ops/state/current_status.md ops/state/backlog.md ops/tasks ops/state/decision_log.md` returned no reserved future ids in this run apart from historical notes.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains no task files in this checkout.
- JSON burn-down remains complete and current in both tracked and live views for this run:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The shared-queue stall rule does not apply in this checkout:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest runtime cycle shows both task workers finishing `done`, with no inherited-dirty checkpoint churn or stalled post-task refresh path.
- The remaining duplication is concrete in the live checkout:
  - `tests/python/test_grouped_capture_parity_suite.py:113` still defines `CASES_BY_ID` from a local `_iter_fixture_cases()` generator;
  - `tests/python/test_branch_local_backreference_parity_suite.py:486` still defines `CASES_BY_ID` from a local `_iter_fixture_cases()` generator;
  - `tests/python/test_conditional_group_exists_parity_suite.py:90` still defines `CASES_BY_ID` from a local `_iter_fixture_cases()` generator;
  - `tests/python/test_literal_flag_parity_suite.py:190` still defines `LITERAL_FLAG_CASES_BY_ID` inline from `LITERAL_FLAG_FIXTURE_BUNDLE.cases`; and
  - `tests/python/test_quantified_alternation_parity_suite.py:374` still defines `COMPILE_CASES_BY_ID` inline from `fixture_cases_for_operation(FIXTURE_BUNDLES, "compile")`.
- The focused verification slice is green in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py -k 'published_fixture_bundles_by_manifest_id or load_single_published_fixture_bundle' tests/python/test_grouped_capture_parity_suite.py::test_match_group_access_rows_remain_on_grouped_capture_fixture_paths tests/python/test_branch_local_backreference_parity_suite.py::test_pattern_bounds_cases_stay_anchored_to_supported_backreference_patterns tests/python/test_conditional_group_exists_parity_suite.py::test_generated_fully_empty_alternation_compile_cases_stay_anchored_to_published_manifest tests/python/test_literal_flag_parity_suite.py::test_literal_ignorecase_module_helpers_match_cpython tests/python/test_quantified_alternation_parity_suite.py::test_compile_metadata_matches_cpython` returned `5 passed, 434 deselected` in this run.
- The negative `rg` verification currently fails exactly on the targeted duplicate lookup maps above, so it is an acceptance check for this cleanup rather than unrelated repo drift.
