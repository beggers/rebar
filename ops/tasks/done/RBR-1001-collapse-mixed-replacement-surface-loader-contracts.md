## RBR-1001: Collapse mixed replacement surface loader contracts

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated mixed-text replacement-surface loader contract scaffolding from `tests/python/test_fixture_backed_replacement_parity_suite.py` so the three narrow `_load_surface(...)` contract tests around the nested broader-range open-ended replacement manifests assert through one smaller file-local helper surface instead of retyping the same selected/uncovered/module/pattern/frontier checks with only minor match-group and template differences.

## Deliverables
- `tests/python/test_fixture_backed_replacement_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_fixture_backed_replacement_parity_suite.py` adds one explicit file-local helper surface for the repeated mixed-text replacement-surface loader assertions, or a strictly smaller equivalent, that centralizes the contract currently open-coded in:
  - `test_broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on()`
  - `test_mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on()`
  - `test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier()`
- Repoint those three tests through that shared helper surface instead of leaving the repeated `str_cases` / `bytes_cases` selection, expected module/pattern case-id derivation, `surface.*_cases` assertions, and frontier checks open-coded in each body.
- Preserve the current mixed-text loader contracts exactly while shrinking the glue:
  - each targeted bundle still resolves to `16` total fixture rows with `Counter({("module_call", "sub"): 4, ("module_call", "subn"): 4, ("pattern_call", "sub"): 4, ("pattern_call", "subn"): 4})` across mixed `str` / `bytes` text models;
  - the two pending-bytes tests still publish only the `8` `str` rows as the selected frontier, still leave the `8` paired `bytes` rows uncovered, and still keep `surface.replacement_cases`, `surface.module_cases`, and `surface.pattern_cases` limited to the selected `str` rows in fixture order;
  - `test_broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on()` still keeps `surface.match_group_access_cases == ()` and `surface.template_expand_cases` equal to the selected `str` rows;
  - `test_mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on()` still keeps both `surface.match_group_access_cases` and `surface.template_expand_cases` equal to the selected `str` rows; and
  - `test_broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier()` still keeps all `16` mixed-text rows selected, still leaves no uncovered rows, still keeps `surface.match_group_access_cases == ()`, and still keeps `surface.template_expand_cases` equal to all selected rows.
- Keep the cleanup structural and file-local:
  - preserve the existing `ReplacementSurfaceSpec`, `_load_surface(...)`, `assert_mixed_text_model_case_pairs(...)`, and `_expected_selected_replacement_case_ids(...)` / `_expected_uncovered_replacement_case_ids(...)` surfaces unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this run into grouped-template ownership assertions above the target block, direct replacement parity parametrization, fixture manifests, correctness harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on or mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on or broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_fixture_backed_replacement_parity_suite import (
    EXPECTED_OPERATION_HELPER_COUNTS,
    MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS,
    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR,
    NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
    NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
    ReplacementSurfaceSpec,
    _load_surface,
    assert_mixed_text_model_case_pairs,
    case_pattern,
    fixture_cases_for_operation,
)

checks = (
    (
        "pending-template-only",
        ReplacementSurfaceSpec(
            id="pending-template-only",
            fixture_selector=NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
            pattern_extractor=case_pattern,
            template_expand_manifest_ids=(
                NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
            ),
            pending_bytes_follow_on_manifest_ids=frozenset(
                {NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID}
            ),
        ),
        EXPECTED_OPERATION_HELPER_COUNTS,
        (),
        "selected-only",
    ),
    (
        "pending-match-and-template",
        ReplacementSurfaceSpec(
            id="pending-match-and-template",
            fixture_selector=(
                NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_FIXTURE_SELECTOR
            ),
            pattern_extractor=case_pattern,
            match_group_access_manifest_ids=(
                NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
            ),
            template_expand_manifest_ids=(
                NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID,
            ),
            pending_bytes_follow_on_manifest_ids=frozenset(
                {NESTED_BROADER_RANGE_OPEN_ENDED_CONDITIONAL_REPLACEMENT_MANIFEST_ID}
            ),
        ),
        EXPECTED_OPERATION_HELPER_COUNTS,
        "selected",
        "selected-only",
    ),
    (
        "full-mixed-template-only",
        ReplacementSurfaceSpec(
            id="full-mixed-template-only",
            fixture_selector=NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_FIXTURE_SELECTOR,
            pattern_extractor=case_pattern,
            template_expand_manifest_ids=(
                NESTED_BROADER_RANGE_OPEN_ENDED_REPLACEMENT_MANIFEST_ID,
            ),
        ),
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS,
        (),
        "all-cases",
    ),
)

for label, spec, expected_counts, expected_match_group, template_mode in checks:
    surface = _load_surface(spec)
    (bundle,) = surface.bundles
    str_cases, bytes_cases = assert_mixed_text_model_case_pairs(bundle)
    selected_ids = tuple(case.case_id for case in str_cases)
    uncovered_ids = tuple(case.case_id for case in bytes_cases)
    all_ids = tuple(case.case_id for case in bundle.cases)
    limited_ids = selected_ids if template_mode == "selected-only" else all_ids
    module_ids = tuple(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "module_call")
        if case.case_id in limited_ids
    )
    pattern_ids = tuple(
        case.case_id
        for case in fixture_cases_for_operation((bundle,), "pattern_call")
        if case.case_id in limited_ids
    )

    assert len(bundle.cases) == 16, label
    assert Counter((case.operation, case.helper) for case in bundle.cases) == (
        MIXED_TEXT_MODEL_OPERATION_HELPER_COUNTS
    ), label
    assert Counter((case.operation, case.helper) for case in surface.replacement_cases) == (
        expected_counts
    ), label

    if template_mode == "selected-only":
        assert tuple(case.case_id for case in surface.replacement_cases) == selected_ids, label
        assert tuple(case.case_id for case in surface.module_cases) == module_ids, label
        assert tuple(case.case_id for case in surface.pattern_cases) == pattern_ids, label
        assert tuple(case.case_id for case in surface.template_expand_cases) == selected_ids, label
        assert len(uncovered_ids) == 8, label
    else:
        assert tuple(case.case_id for case in surface.replacement_cases) == all_ids, label
        assert tuple(case.case_id for case in surface.module_cases) == tuple(
            case.case_id for case in fixture_cases_for_operation((bundle,), "module_call")
        ), label
        assert tuple(case.case_id for case in surface.pattern_cases) == tuple(
            case.case_id for case in fixture_cases_for_operation((bundle,), "pattern_call")
        ), label
        assert tuple(case.case_id for case in surface.template_expand_cases) == all_ids, label
        assert len(uncovered_ids) == 8, label

    if expected_match_group == "selected":
        assert tuple(case.case_id for case in surface.match_group_access_cases) == selected_ids, label
    else:
        assert tuple(case.case_id for case in surface.match_group_access_cases) == expected_match_group, label

print("ok")
PY`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_fixture_backed_replacement_parity_suite.py`.
- Prefer deleting repeated mixed-text surface-loader glue over introducing another abstraction layer.
- Do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-replacement parity test files in this run.

## Notes
- `RBR-1001` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1001|RBR-1002|RBR-1003|RBR-1004|RBR-1005' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-1000-catch-up-pattern-replacement-bytes-single-match-repeated-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`3 passed, 1295 deselected`);
  - the contract probe in Verification currently passes (`ok`); and
  - `tests/python/test_fixture_backed_replacement_parity_suite.py` currently repeats the same `expected_selected_case_ids = tuple(case.case_id for case in str_cases)`, `expected_uncovered_case_ids = tuple(case.case_id for case in bytes_cases)`, expected module/pattern derivation, and frontier assertions across the three target tests at lines `1846`, `1847`, `1907`, `1908`, and the surrounding assertion blocks through line `1979`, so this cleanup can stay structural and file-local.
- 2026-03-23 completion:
  - added the file-local `MixedTextReplacementSurfaceContract` plus `_assert_mixed_text_replacement_surface_loader_contract(...)` helper in `tests/python/test_fixture_backed_replacement_parity_suite.py` to centralize the repeated mixed-text bundle, selected/uncovered frontier, and module/pattern loader assertions for the three targeted tests;
  - repointed the three target tests through that helper while keeping their specific `match_group_access_cases` and `template_expand_cases` expectations explicit;
  - verified `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_fixture_backed_replacement_parity_suite.py -k 'broader_range_open_ended_replacement_manifest_can_stage_bytes_as_pending_follow_on or mixed_replacement_manifest_can_stage_bytes_as_pending_follow_on or broader_range_open_ended_replacement_manifest_no_longer_filters_bytes_from_selected_frontier'` (`3 passed, 1295 deselected`); and
  - verified the task's contract probe script (`ok`).
