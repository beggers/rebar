# RBR-0993: Collapse positional-indexlike publication contract assertions

Status: done
Owner: cleanup
Created: 2026-03-23

## Goal
- Remove the remaining duplicated positional-indexlike publication-contract scaffolding from `tests/python/test_module_workflow_parity_suite.py` so the module and pattern slices assert through one smaller file-local helper instead of repeating the same fixture selection, ordering, and helper-count checks inline.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for positional-indexlike publication contracts, or a strictly smaller equivalent, that centralizes the repeated setup currently open-coded in these tests:
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases()`
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases()`
- Repoint those two tests through the shared helper surface instead of repeating the same `_published_positional_indexlike_fixture_cases(...)` / `_selected_positional_indexlike_direct_cases(...)` setup and shared ordering/count assertions inline.
- Preserve the current live publication contracts exactly while removing the repeated assertion scaffolding:
  - the module positional-indexlike slice still resolves to `3` published fixture rows and `3` selected direct rows, with `Counter({"split": 1, "sub": 1, "subn": 1})`;
  - the module `str` fixture split still stays `("workflow-module-sub-count-indexlike-positional-str",)`;
  - the module `bytes` fixture split still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module published fixture order still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-sub-count-indexlike-positional-str", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module selected direct-case order still stays `("module-split-maxsplit-indexlike-positional-bytes", "module-sub-count-indexlike-positional-str", "module-subn-count-indexlike-positional-bytes")`;
  - the pattern positional-indexlike slice still resolves to `9` published fixture rows and `9` selected direct rows, with `Counter({"search": 2, "match": 1, "fullmatch": 1, "findall": 1, "finditer": 1, "split": 1, "sub": 1, "subn": 1})`;
  - the pattern `str` fixture split still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-subn-count-indexlike-positional-str")`;
  - the pattern `bytes` fixture split still stays `("workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes")`;
  - the pattern published fixture order still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes", "workflow-pattern-subn-count-indexlike-positional-str")`; and
  - the pattern selected direct-case order still stays `("pattern-search-pos-indexlike-positional-str", "pattern-search-endpos-indexlike-positional-bytes", "pattern-match-window-indexlike-positional-bytes", "pattern-fullmatch-window-indexlike-positional-bytes", "pattern-findall-window-indexlike-positional-str", "pattern-finditer-window-indexlike-positional-bytes", "pattern-split-maxsplit-indexlike-positional-str", "pattern-sub-count-indexlike-positional-bytes", "pattern-subn-count-indexlike-positional-str")`.
- Keep the cleanup structural and file-local:
  - keep `_published_positional_indexlike_fixture_cases(...)`, `_selected_positional_indexlike_direct_cases(...)`, `_fixture_cases_for_text_model(...)`, and the existing direct/publication tests as the canonical live selector surface unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into positional-indexlike selector cleanup, owner-path helpers, bounded-wildcard helpers, manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_CALL_CASES,
    MODULE_POSITIONAL_INDEXLIKE_CALL_CASES,
    PATTERN_CASES,
    PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES,
    _assert_positional_indexlike_publication_contract,
)

module_published, module_selected = _assert_positional_indexlike_publication_contract(
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
assert len(module_published) == len(module_selected) == 3

pattern_published, pattern_selected = _assert_positional_indexlike_publication_contract(
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
assert len(pattern_published) == len(pattern_selected) == 9
print("ok")
PY`

## Notes
- `RBR-0993` was unreserved in tracked queue/state files when this cleanup started:
  - `rg -n 'RBR-0993|RBR-0994|RBR-0995' ops/tasks ops/state/current_status.md ops/state/backlog.md` returned matches only inside prior done-task notes that documented then-future ids, and no live reservation in ready/in-progress/blocked work.
- The target file was clean before editing:
  - `git status --short -- tests/python/test_module_workflow_parity_suite.py` returned no output.
- This cleanup preserves the landed selector shape from `RBR-0984` and only removes repeated publication-contract assertions layered on top of those selectors.

## Completion
- Added `_assert_positional_indexlike_publication_contract(...)` to `tests/python/test_module_workflow_parity_suite.py` so the module and pattern positional-indexlike publication tests share one file-local setup and contract assertion path.
- Repointed the two positional-indexlike publication tests through that helper while keeping their fixture-vs-direct-case field assertions local and unchanged in behavior.
- Verified with the focused pytest slice and the explicit positional-indexlike contract probe.
