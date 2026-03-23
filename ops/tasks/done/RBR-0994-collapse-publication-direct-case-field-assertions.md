## RBR-0994: Collapse publication direct-case field assertions

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the repeated fixture-vs-direct-case field-alignment loops from `tests/python/test_module_workflow_parity_suite.py` so the non-compiled publication slices assert through one smaller file-local helper surface, or a strictly smaller equivalent, instead of open-coding the same per-row shape checks across seven tests.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for non-compiled publication field alignment, or a strictly smaller equivalent, that centralizes the repeated row-by-row assertions currently open-coded in these tests:
  - `test_module_workflow_surface_publishes_module_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_helpers_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_keyword_error_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_wrong_text_model_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases()`
- Repoint those seven tests through the shared helper surface instead of repeating their current `for fixture_case, direct_case in zip(...)` loops and the same field-by-field assertions inline.
- Preserve the current live field-alignment contracts exactly while removing the repeated scaffolding:
  - the two module keyword publication slices still verify `use_compiled_pattern is False`, derive `text_model` from the direct pattern argument, keep `case_pattern(fixture_case) == direct_pattern`, keep `tuple(fixture_case.args) == tuple(direct_args)`, keep keyword-argument signatures aligned through `_workflow_keyword_kwargs_signature(...)`, and keep `fixture_case.flags == 0`;
  - the three pattern keyword publication slices still verify `text_model` from `direct_case.pattern`, keep `case_pattern(fixture_case) == direct_case.pattern`, keep `tuple(fixture_case.args) == direct_case.args`, keep keyword-argument signatures aligned through `_workflow_keyword_kwargs_signature(...)`, and keep `fixture_case.flags == 0`;
  - the module positional-indexlike publication slice still verifies `include_pattern_arg is True`, `use_compiled_pattern is False`, `text_model` from the direct pattern argument, `case_pattern(fixture_case) == direct_pattern`, positional-argument signatures aligned through `_workflow_positional_args_signature(...)`, `fixture_case.kwargs == {}`, and `fixture_case.flags == 0`;
  - the pattern positional-indexlike publication slice still verifies `text_model` from `direct_case.pattern`, `case_pattern(fixture_case) == direct_case.pattern`, positional-argument signatures aligned through `_workflow_positional_args_signature(...)`, `fixture_case.kwargs == {}`, and `fixture_case.flags == 0`.
- Keep the cleanup structural and file-local:
  - keep `_assert_owner_path_publication_contract(...)` and `_assert_positional_indexlike_publication_contract(...)` as the canonical selection/count contract helpers unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into the bounded-wildcard raw-module helper publication test, the compiled-pattern module-helper publication test, selector tables, fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'publishes_module_keyword_helpers_from_direct_cases or publishes_module_keyword_error_slice_from_direct_cases or publishes_pattern_keyword_helpers_from_direct_cases or publishes_pattern_keyword_error_slice_from_direct_cases or publishes_pattern_wrong_text_model_slice_from_direct_cases or publishes_module_positional_indexlike_slice_from_direct_cases or publishes_pattern_positional_indexlike_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_CALL_CASES,
    RAW_MODULE_CALL_CASES,
    PATTERN_CASES,
    MODULE_POSITIONAL_INDEXLIKE_CALL_CASES,
    PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES,
    MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
    PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
    _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
    _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
    _assert_owner_path_publication_contract,
    _assert_positional_indexlike_publication_contract,
)

for published_fixture_cases, selected_direct_cases in (
    _assert_owner_path_publication_contract(
        RAW_MODULE_CALL_CASES,
        MODULE_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        expected_count=14,
        expected_text_model_counts=Counter({"str": 6, "bytes": 8}),
        expected_helper_counts=Counter(
            {"search": 1, "match": 1, "fullmatch": 1, "split": 3, "sub": 4, "subn": 4}
        ),
    ),
    _assert_owner_path_publication_contract(
        RAW_MODULE_CALL_CASES,
        MODULE_KEYWORD_ERROR_PUBLICATION_OWNER_PATH_ROWS,
        expected_count=13,
        expected_text_model_counts=Counter({"str": 8, "bytes": 5}),
        expected_helper_counts=Counter(
            {"search": 1, "split": 3, "sub": 4, "fullmatch": 1, "subn": 4}
        ),
    ),
    _assert_owner_path_publication_contract(
        PATTERN_CASES,
        PATTERN_KEYWORD_PUBLICATION_OWNER_PATH_ROWS,
        expected_count=27,
        expected_text_model_counts=Counter({"str": 15, "bytes": 12}),
        expected_helper_counts=Counter(
            {
                "search": 5,
                "match": 3,
                "fullmatch": 2,
                "findall": 3,
                "finditer": 3,
                "split": 3,
                "sub": 4,
                "subn": 4,
            }
        ),
    ),
    _assert_owner_path_publication_contract(
        PATTERN_CASES,
        _PATTERN_KEYWORD_ERROR_OWNER_PATH_ROWS,
        expected_count=10,
        expected_helper_counts=Counter({"split": 2, "sub": 4, "subn": 4}),
    ),
    _assert_owner_path_publication_contract(
        PATTERN_CASES,
        _PATTERN_WRONG_TEXT_MODEL_OWNER_PATH_ROWS,
        expected_count=6,
        expected_text_model_counts=Counter({"str": 4, "bytes": 2}),
        expected_helper_counts=Counter(
            {"search": 1, "match": 1, "fullmatch": 1, "split": 1, "sub": 1, "subn": 1}
        ),
    ),
):
    assert len(published_fixture_cases) == len(selected_direct_cases)

module_positional = _assert_positional_indexlike_publication_contract(
    MODULE_CALL_CASES,
    MODULE_POSITIONAL_INDEXLIKE_CALL_CASES,
    expected_str_case_ids=("workflow-module-sub-count-indexlike-positional-str",),
    expected_bytes_case_ids=(
        "workflow-module-split-maxsplit-indexlike-positional-bytes",
        "workflow-module-subn-count-indexlike-positional-bytes",
    ),
    expected_published_case_ids=(
        "workflow-module-split-maxsplit-indexlike-positional-bytes",
        "workflow-module-sub-count-indexlike-positional-str",
        "workflow-module-subn-count-indexlike-positional-bytes",
    ),
    expected_direct_case_ids=(
        "module-split-maxsplit-indexlike-positional-bytes",
        "module-sub-count-indexlike-positional-str",
        "module-subn-count-indexlike-positional-bytes",
    ),
    expected_helper_counts=Counter({"split": 1, "sub": 1, "subn": 1}),
)
pattern_positional = _assert_positional_indexlike_publication_contract(
    PATTERN_CASES,
    PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES,
    expected_str_case_ids=(
        "workflow-pattern-search-str-pos-indexlike-positional",
        "workflow-pattern-findall-str-window-indexlike-positional",
        "workflow-pattern-split-str-maxsplit-indexlike-positional",
        "workflow-pattern-subn-count-indexlike-positional-str",
    ),
    expected_bytes_case_ids=(
        "workflow-pattern-search-bytes-endpos-indexlike-positional",
        "workflow-pattern-match-bytes-window-indexlike-positional",
        "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
        "workflow-pattern-finditer-bytes-window-indexlike-positional",
        "workflow-pattern-sub-count-indexlike-positional-bytes",
    ),
    expected_published_case_ids=(
        "workflow-pattern-search-str-pos-indexlike-positional",
        "workflow-pattern-search-bytes-endpos-indexlike-positional",
        "workflow-pattern-match-bytes-window-indexlike-positional",
        "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
        "workflow-pattern-findall-str-window-indexlike-positional",
        "workflow-pattern-finditer-bytes-window-indexlike-positional",
        "workflow-pattern-split-str-maxsplit-indexlike-positional",
        "workflow-pattern-sub-count-indexlike-positional-bytes",
        "workflow-pattern-subn-count-indexlike-positional-str",
    ),
    expected_direct_case_ids=(
        "pattern-search-pos-indexlike-positional-str",
        "pattern-search-endpos-indexlike-positional-bytes",
        "pattern-match-window-indexlike-positional-bytes",
        "pattern-fullmatch-window-indexlike-positional-bytes",
        "pattern-findall-window-indexlike-positional-str",
        "pattern-finditer-window-indexlike-positional-bytes",
        "pattern-split-maxsplit-indexlike-positional-str",
        "pattern-sub-count-indexlike-positional-bytes",
        "pattern-subn-count-indexlike-positional-str",
    ),
    expected_helper_counts=Counter(
        {
            "search": 2,
            "match": 1,
            "fullmatch": 1,
            "findall": 1,
            "finditer": 1,
            "split": 1,
            "sub": 1,
            "subn": 1,
        }
    ),
    include_fixture_case=lambda case: case.kwargs == {},
)
assert len(module_positional[0]) == len(module_positional[1]) == 3
assert len(pattern_positional[0]) == len(pattern_positional[1]) == 9
print("ok")
PY`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting repeated assertion glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0994` is the next available task id in the current checkout:
  - `rg -n 'RBR-0994|RBR-0995|RBR-0996|RBR-0997|RBR-0998|RBR-0999|RBR-1000' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0993-collapse-positional-indexlike-publication-contract-assertions.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'publishes_module_keyword_helpers_from_direct_cases or publishes_module_keyword_error_slice_from_direct_cases or publishes_pattern_keyword_helpers_from_direct_cases or publishes_pattern_keyword_error_slice_from_direct_cases or publishes_pattern_wrong_text_model_slice_from_direct_cases or publishes_module_positional_indexlike_slice_from_direct_cases or publishes_pattern_positional_indexlike_slice_from_direct_cases'` currently passes (`7 passed, 1444 deselected`);
  - the verification probe above currently passes (`ok`); and
  - `python3 - <<'PY'
from pathlib import Path
text = Path("tests/python/test_module_workflow_parity_suite.py").read_text().splitlines()
for i, line in enumerate(text, start=1):
    if "for fixture_case, direct_case in zip(published_fixture_cases, selected_direct_cases):" in line:
        print(i)
PY` currently reports repeated open-coded loops at lines `4703`, `4738`, `4808`, `4841`, and `5047`, while the companion publication tests at `4645` and `4771` carry the same shape through a multi-line `zip(...)` call.

## Completion
- Added `_assert_noncompiled_publication_direct_case_field_alignment(...)` to `tests/python/test_module_workflow_parity_suite.py` so the seven non-compiled owner-path and positional publication slices share one file-local field-alignment assertion path.
- Repointed the seven scoped publication tests through that helper while preserving the existing per-slice contracts for `text_model`, pattern identity, args or positional signatures, kwargs signatures, `include_pattern_arg`, `use_compiled_pattern`, and `flags`.
- Verified with the focused pytest selection from this task (`7 passed, 1444 deselected`) and the explicit publication-contract probe (`ok`).
