# RBR-0416: Centralize correctness fixture selectors in the harness

Status: done
Owner: architecture-implementation
Created: 2026-03-15
Completed: 2026-03-15

## Goal
- Replace the current correctness-fixture inventory path arithmetic with one small shared selector surface in `python/rebar_harness/correctness.py`, so the default scorecard harness and the focused Python parity suites stop hand-maintaining sorted filename tuples, path filtering, and callable-fixture globbing.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/conformance/test_correctness_fixture_inventory_contract.py`
- `tests/python/fixture_parity_support.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/python/test_counted_repeat_quantified_group_parity_suite.py`
- `tests/python/test_quantified_alternation_parity_suite.py`
- `tests/python/test_bounded_wildcard_parity_suite.py`
- `tests/python/test_simple_backreference_parity_suite.py`
- `tests/python/test_conditional_group_exists_replacement_parity_suite.py`
- `tests/python/test_grouped_capture_parity_suite.py`
- `tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py`
- `tests/python/test_branch_local_backreference_parity_suite.py`
- `tests/python/test_literal_flag_parity_suite.py`
- `tests/python/test_callable_replacement_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py`
- `tests/python/test_open_ended_quantified_group_parity_suite.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` exposes one shared correctness-fixture selector surface rooted at a single fixtures-directory constant. That selector surface owns:
  - the published full-suite default inventory used by the correctness CLI; and
  - the focused published fixture packs currently spelled out as local filename/path tuples in the updated `tests/python` parity suites.
- `DEFAULT_FIXTURE_PATHS` is derived from the published full-suite selector rather than an open-coded tuple of repeated `REPO_ROOT / "tests" / "conformance" / "fixtures" / ...` joins.
- `tests/python/fixture_parity_support.py` no longer owns published-fixture path selection. Remove `select_published_fixture_paths()` and keep only the generic case, pattern, and parity helpers there.
- Each updated suite module listed above resolves its published fixture pack through the shared correctness selector surface rather than local `EXPECTED_PUBLISHED_FIXTURE_NAMES` blocks, sorted path tuples, or equivalent directory filtering.
- `tests/python/test_callable_replacement_parity_suite.py` resolves the published callable-replacement fixture pack through the shared selector surface rather than `FIXTURES_DIR.glob("*callable_replacement_workflows.py")` plus filtering.
- Selector-driven inventory behavior stays unchanged after the cleanup:
  - the published full-suite selector resolves to the current `DEFAULT_FIXTURE_PATHS` membership and ordering;
  - each updated focused suite resolves the same published fixture-path set it asserted before the cleanup; and
  - no selector returns a path outside `tests/conformance/fixtures/`.
- `tests/conformance/test_correctness_fixture_inventory_contract.py` adds contract coverage for the published full-suite selector instead of only checking the raw `DEFAULT_FIXTURE_PATHS` tuple.
- `tests/python/test_fixture_parity_support_contract.py` replaces the old filter/sort helper contract with selector contract coverage, including an unknown-selector failure path.
- After the cleanup, `rg -n 'select_published_fixture_paths|EXPECTED_PUBLISHED_FIXTURE_NAMES|glob\\("\\*callable_replacement_workflows\\.py"\\)' tests/python python/rebar_harness/correctness.py` returns no matches.
- Verification passes with `PYTHONPATH=python .venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_conditional_group_exists_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py`.

## Constraints
- Keep this task on correctness inventory plumbing only. Do not change Rust code, `python/rebar/`, correctness fixture contents, benchmark workloads, published reports, README reporting, or tracked state files beyond this task file.
- Prefer small selector helpers inside `python/rebar_harness/correctness.py` over adding a new registry module, package-discovery layer, or generated inventory file.
- Preserve current published full-suite ordering and the existing focused-suite fixture membership. This cleanup should delete duplicate selector plumbing, not broaden or shrink coverage.

## Notes
- This is the correctness-side mirror of `RBR-0413`: benchmarks now have named inventory selectors, but correctness still leaks published fixture membership into a dozen `tests/python` modules through repeated `EXPECTED_PUBLISHED_FIXTURE_NAMES` blocks and one-off filtering.
- The runtime dashboard is clean and both tracked and live JSON counts are zero (`tracked_json_blob_count: 0`, `tracked_json_blob_delta: 0`, `git ls-files '*.json' | wc -l = 0`, `rg --files -g '*.json' | wc -l = 0`), so this run should seed a post-JSON duplicate-plumbing cleanup rather than another JSON burn-down task.

## Completion
- 2026-03-15: Added named correctness fixture selectors in `python/rebar_harness/correctness.py`, re-rooted selector results through `CORRECTNESS_FIXTURES_ROOT`, and derived `DEFAULT_FIXTURE_PATHS` from the published full-suite selector while preserving the existing default full-suite ordering.
- 2026-03-15: Removed published-fixture selection from `tests/python/fixture_parity_support.py`, switched the targeted parity suites to the shared selector API, and replaced the old helper contract with centralized selector coverage plus an unknown-selector failure check.

## Verification
- 2026-03-15: `PYTHONPATH=python .venv/bin/python -m pytest -q tests/conformance/test_correctness_fixture_inventory_contract.py tests/python/test_fixture_parity_support_contract.py tests/python/test_counted_repeat_quantified_group_parity_suite.py tests/python/test_quantified_alternation_parity_suite.py tests/python/test_bounded_wildcard_parity_suite.py tests/python/test_simple_backreference_parity_suite.py tests/python/test_conditional_group_exists_replacement_parity_suite.py tests/python/test_grouped_capture_parity_suite.py tests/python/test_wider_ranged_repeat_quantified_group_parity_suite.py tests/python/test_branch_local_backreference_parity_suite.py tests/python/test_literal_flag_parity_suite.py tests/python/test_callable_replacement_parity_suite.py tests/python/test_open_ended_quantified_group_replacement_template_parity_suite.py tests/python/test_open_ended_quantified_group_parity_suite.py` (`3575 passed, 44 skipped, 1141 subtests passed`)
- 2026-03-15: `rg -n 'select_published_fixture_paths|EXPECTED_PUBLISHED_FIXTURE_NAMES|glob\("\*callable_replacement_workflows\.py"\)' tests/python python/rebar_harness/correctness.py` (no matches)
