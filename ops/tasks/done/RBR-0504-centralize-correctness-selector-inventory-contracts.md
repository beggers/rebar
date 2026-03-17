# RBR-0504: Centralize correctness selector inventory contracts

Status: done
Owner: architecture-implementation
Created: 2026-03-17

## Goal
- Move the remaining exact selector-membership checks for shared correctness fixture selectors into `tests/python/test_fixture_parity_support_contract.py`, and delete the suite-local selector/path assertions that only restate that shared contract. The intended end state is one obvious selector-inventory contract plus parity suites that keep only bundle-shape and frontier coverage.

## Deliverables
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_bounded_wildcard_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_callable_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_parity_support_contract.py` becomes the single exact-membership surface for the shared correctness selectors currently mirrored by suite-local equality checks:
  - keep the existing exact filename expectations for the selectors already covered there;
  - add exact filename expectations for `CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR` and `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR` using the current live selector order; and
  - delete the naming-predicate-only replacement-selector layer (`_is_conditional_replacement_fixture_name(...)`, `_is_callable_replacement_fixture_name(...)`, and `REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS`) so selector inventory drift is pinned by one exact filename table rather than a mix of exact tuples and pattern heuristics.
- The touched parity suites stop duplicating selector inventory checks while preserving their unique coverage:
  - delete the redundant suite-local selector/path tests now covered by the shared contract:
    - `test_counted_repeat_quantified_group_suite_uses_expected_published_fixtures`
    - `test_alternation_parity_suite_uses_expected_published_fixtures`
    - `test_bounded_wildcard_suite_uses_expected_published_fixture_paths`
    - `test_replacement_template_parity_suite_uses_expected_published_fixture_paths`
    - `test_grouped_capture_parity_suite_uses_expected_published_fixture_paths`
    - `test_simple_backreference_suite_uses_expected_published_fixture_paths`
    - `test_parity_suite_uses_expected_published_fixture_paths` in `test_wider_ranged_repeat_quantified_group_parity_suite.py`
    - `test_open_ended_quantified_group_suite_uses_expected_published_fixture_paths`
    - `test_expected_branch_local_backreference_fixtures_remain_published`
    - the selector-equality portion of `test_literal_flag_suite_stays_aligned_with_published_correctness_fixture`
    - `test_callable_replacement_suite_discovers_all_published_callable_fixtures`
  - keep `assert_fixture_bundle_contract(...)` coverage in those suites;
  - keep the non-redundant frontier checks, such as the literal-flag delegated-case assertions and the conditional-replacement uncovered-path assertions; and
  - keep `CALLABLE_FIXTURE_PATHS` in `tests/python/test_callable_replacement_parity_suite.py` if it is still needed to drive `load_published_fixture_bundles(...)`, but do not retain it just for an equality-only assertion.
- Remove the now-unused selector boilerplate from the touched suites:
  - delete the `PUBLISHED_*_FIXTURE_PATHS = select_correctness_fixture_paths(...)` constants from the touched suites where those constants only existed for the removed selector-equality tests; and
  - remove any now-unused `select_correctness_fixture_paths` / `published_fixture_paths_from_bundles` imports from those files.
- Preserve current behavior exactly:
  - do not change fixture modules under `tests/conformance/fixtures/`;
  - do not change `python/rebar_harness/correctness.py` selector behavior or published fixture ordering;
  - do not change the bundle specs, selected case ids, bundle manifest ids, or parity coverage frontier in the touched suites; and
  - do not broaden into benchmark tests, feature work, or correctness-harness loader changes.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
  - ```bash
    PYTHONPATH=python ./.venv/bin/python - <<'PY'
    from rebar_harness.correctness import (
        CALLABLE_REPLACEMENT_FIXTURE_SELECTOR,
        CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR,
        select_correctness_fixture_paths,
    )

    callable_expected = [
        "conditional_group_exists_callable_replacement_workflows.py",
        "grouped_alternation_callable_replacement_workflows.py",
        "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
        "nested_broader_range_open_ended_quantified_group_alternation_branch_local_backreference_conditional_callable_replacement_workflows.py",
        "nested_broader_range_wider_ranged_repeat_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
        "nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
        "nested_group_alternation_callable_replacement_workflows.py",
        "nested_group_callable_replacement_workflows.py",
        "nested_open_ended_quantified_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
        "quantified_nested_group_alternation_branch_local_backreference_callable_replacement_workflows.py",
        "quantified_nested_group_alternation_callable_replacement_workflows.py",
        "quantified_nested_group_callable_replacement_workflows.py",
    ]
    conditional_expected = [
        "conditional_group_exists_alternation_replacement_workflows.py",
        "conditional_group_exists_empty_else_replacement_workflows.py",
        "conditional_group_exists_empty_yes_else_replacement_workflows.py",
        "conditional_group_exists_fully_empty_replacement_workflows.py",
        "conditional_group_exists_nested_replacement_workflows.py",
        "conditional_group_exists_no_else_replacement_workflows.py",
        "conditional_group_exists_quantified_alternation_replacement_workflows.py",
        "conditional_group_exists_quantified_replacement_workflows.py",
        "conditional_group_exists_replacement_template_workflows.py",
        "conditional_group_exists_replacement_workflows.py",
    ]

    assert [path.name for path in select_correctness_fixture_paths(CALLABLE_REPLACEMENT_FIXTURE_SELECTOR)] == callable_expected
    assert [path.name for path in select_correctness_fixture_paths(CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR)] == conditional_expected
    print("ok")
    PY
    ```
  - `rg -n "uses_expected_published_fixture_paths|uses_expected_published_fixtures|discovers_all_published_callable_fixtures|expected_branch_local_backreference_fixtures_remain_published" tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py`
    The post-change result must be no matches.
  - `rg -n '_is_conditional_replacement_fixture_name|_is_callable_replacement_fixture_name|REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS' tests/python/test_fixture_parity_support_contract.py`
    The post-change result must be no matches.
  - `rg -n 'PUBLISHED_[A-Z_]+FIXTURE_PATHS = select_correctness_fixture_paths\\(' tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py`
    The post-change result must be no matches.

## Constraints
- Keep this cleanup structural only. Do not change fixture filenames, selector order in `python/rebar_harness/correctness.py`, published reports, README text, or tracked state files.
- Prefer deleting duplicated suite-local assertions over adding another helper layer or moving selector inventory into the parity suites again.
- Do not broaden into conditional-replacement frontier reshaping, callable replacement semantics, or any feature/parity change.

## Notes
- `RBR-0503` is reserved in `ops/state/backlog.md` and `ops/state/current_status.md`, and `RBR-0504` is unused in the tracked queue/state.
- No blocked architecture task is waiting to be reopened or normalized in the current checkout.
- JSON burn-down remains complete in both tracked and live views:
  - `tracked_json_blob_count: 0`
  - `tracked_json_blob_delta: 0`
  - `git ls-files '*.json' | wc -l = 0`
  - `rg --files -g '*.json' | wc -l = 0`
- Rule 10 does not apply in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are all empty;
  - `.rebar/runtime/dashboard.md` shows no last-cycle anomalies; and
  - the dirty worktree is limited to inherited supervisor/reporting files (`README.md`, `scripts/rebar_ops.py`), not a stalled queue/commit path.
- The current duplicate surface is concrete rather than speculative:
  - `rg -n "uses_expected_published_fixture_paths|uses_expected_published_fixtures|discovers_all_published_callable_fixtures|expected_branch_local_backreference_fixtures_remain_published|PUBLISHED_[A-Z_]+FIXTURE_PATHS = select_correctness_fixture_paths\\(" ...` returns `19` live matches across the 11 touched parity-suite files.
  - `tests/python/test_fixture_parity_support_contract.py` still keeps the replacement selectors on a naming-predicate path instead of the exact filename table, via `_is_conditional_replacement_fixture_name(...)`, `_is_callable_replacement_fixture_name(...)`, and `REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS`.
- 2026-03-17 architecture probes from the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` passes in the current checkout (`3728 passed, 10 skipped in 2.70s`).
  - The callable/conditional selector probe above currently prints the exact filename lists used in the acceptance snippet, so the task can centralize those values without guessing.
  - The two `rg -n ...` cleanup probes above currently return the duplicate test names, selector constants, and replacement-selector helper matches listed in the notes, which is the exact redundant surface this task should delete.

## Completion Notes
- 2026-03-17: Centralized the remaining shared selector inventories in `tests/python/test_fixture_parity_support_contract.py` by adding exact filename tables for `CONDITIONAL_GROUP_EXISTS_REPLACEMENT_FIXTURE_SELECTOR` and `CALLABLE_REPLACEMENT_FIXTURE_SELECTOR`, then deleting the naming-predicate helper path and its dedicated test.
- Removed the selector/path equality tests from the 11 touched parity suites and trimmed the now-unused `select_correctness_fixture_paths(...)`, `published_fixture_paths_from_bundles(...)`, and `PUBLISHED_*_FIXTURE_PATHS` boilerplate where those names only existed to restate the shared contract.
- Kept the bundle-shape and frontier coverage intact, including `assert_fixture_bundle_contract(...)` checks, the literal-flag delegated-case assertions, the callable bundle-loading path through `CALLABLE_FIXTURE_PATHS`, and the existing conditional-replacement frontier assertions.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py` (`3718 passed, 10 skipped in 2.84s`).
  - The task's callable/conditional selector probe prints `ok`.
  - `rg -n "uses_expected_published_fixture_paths|uses_expected_published_fixtures|discovers_all_published_callable_fixtures|expected_branch_local_backreference_fixtures_remain_published" ...` returned no matches across the touched parity suites.
  - `rg -n '_is_conditional_replacement_fixture_name|_is_callable_replacement_fixture_name|REPLACEMENT_SELECTOR_PATTERN_EXPECTATIONS' tests/python/test_fixture_parity_support_contract.py` returned no matches.
  - `rg -n 'PUBLISHED_[A-Z_]+FIXTURE_PATHS = select_correctness_fixture_paths\\(' ...` returned no matches across the touched suite files.
