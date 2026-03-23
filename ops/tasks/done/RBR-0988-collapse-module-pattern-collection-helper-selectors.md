# RBR-0988: Collapse module/pattern collection helper selectors

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the duplicated module-vs-pattern collection helper selectors from `tests/python/test_module_workflow_parity_suite.py` so the literal collection owner derives both published helper slices through one smaller file-local selector surface over the existing published fixture cases instead of carrying two near-identical wrappers.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines the duplicated collection selector helpers:
  - `_published_module_collection_cases_for_helper(...)`
  - `_published_pattern_collection_cases_for_helper(...)`
- Replace that duplicated pair with one explicit but smaller file-local selector surface that reuses the existing collection fixture owner data:
  - `MODULE_COLLECTION_CASES` derives its published `split`, `findall`, and `finditer` rows from the shared selector surface before its existing supplemental direct cases instead of calling a module-specific helper;
  - `PATTERN_COLLECTION_CASES` derives its published `split`, `findall`, and `finditer` rows from the same shared selector surface before its existing supplemental direct cases instead of calling a pattern-specific helper; and
  - `test_literal_collection_direct_test_buckets_cover_selected_frontier()` derives the six module/pattern helper buckets from that same shared selector surface instead of the removed wrappers.
- Preserve the current live collection publication contracts exactly while removing the duplicate helper pair:
  - `_published_collection_fixture_cases()` still resolves, in this order, to:
    - `module-split-str-leading-trailing`
    - `module-split-str-no-match`
    - `module-split-str-pattern-on-bytes-string`
    - `pattern-split-str-no-match`
    - `pattern-split-str-repeated`
    - `pattern-split-bytes-maxsplit`
    - `module-findall-bytes-repeated`
    - `module-findall-str-pattern-on-bytes-string`
    - `pattern-findall-str-no-match`
    - `pattern-findall-str-bounded`
    - `pattern-findall-str-bounded-no-match`
    - `pattern-findall-bytes-bounded`
    - `pattern-findall-bytes-pattern-on-str-string`
    - `module-finditer-str-repeated`
    - `pattern-finditer-str-bounded`
    - `pattern-finditer-str-bounded-no-match`
    - `pattern-finditer-bytes-bounded`
    - `pattern-finditer-bytes-pattern-on-str-string`
    - `module-findall-nonliteral-str`
  - the module helper-backed published slices still resolve, in order, to:
    - `split`: `module-split-str-leading-trailing`, `module-split-str-no-match`
    - `findall`: `module-findall-bytes-repeated`, `module-findall-nonliteral-str`
    - `finditer`: `module-finditer-str-repeated`
  - the pattern helper-backed published slices still resolve, in order, to:
    - `split`: `pattern-split-str-no-match`, `pattern-split-str-repeated`, `pattern-split-bytes-maxsplit`
    - `findall`: `pattern-findall-str-no-match`, `pattern-findall-str-bounded`, `pattern-findall-str-bounded-no-match`, `pattern-findall-bytes-bounded`
    - `finditer`: `pattern-finditer-str-bounded`, `pattern-finditer-str-bounded-no-match`, `pattern-finditer-bytes-bounded`
  - `MODULE_COLLECTION_CASES` still resolves to these `12` case ids in order:
    - `module-split-str-leading-trailing`
    - `module-split-str-no-match`
    - `module-split-str-maxsplit-one`
    - `module-split-str-negative-maxsplit`
    - `module-split-bytes-maxsplit-one`
    - `module-findall-bytes-repeated`
    - `module-findall-nonliteral-str`
    - `module-findall-str-repeated`
    - `module-findall-str-no-match`
    - `module-finditer-str-repeated`
    - `module-finditer-str-no-match`
    - `module-finditer-bytes-repeated`
  - `PATTERN_COLLECTION_CASES` still resolves to these `19` case ids in order:
    - `pattern-split-str-no-match`
    - `pattern-split-str-repeated`
    - `pattern-split-bytes-maxsplit`
    - `pattern-split-str-no-match`
    - `pattern-split-str-repeated`
    - `pattern-split-str-maxsplit-one`
    - `pattern-split-str-negative-maxsplit`
    - `pattern-findall-str-no-match`
    - `pattern-findall-str-bounded`
    - `pattern-findall-str-bounded-no-match`
    - `pattern-findall-bytes-bounded`
    - `pattern-findall-str-bounded`
    - `pattern-findall-str-bounded-no-match`
    - `pattern-findall-bytes-bounded`
    - `pattern-finditer-str-bounded`
    - `pattern-finditer-str-bounded-no-match`
    - `pattern-finditer-bytes-bounded`
    - `pattern-finditer-str-bounded`
    - `pattern-finditer-str-bounded-no-match`
- Keep the cleanup structural and file-local:
  - keep `_published_collection_fixture_cases()`, `_module_collection_case_from_fixture(...)`, `_pattern_collection_case_from_fixture(...)`, and `_is_collection_type_error_fixture_case(...)` as the canonical live owner surfaces unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into bounded-wildcard helpers, owner-path selectors, positional-indexlike selectors, compiled-pattern module-helper selectors, fixture manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.
- The structural simplification is visible in the file:
  - `rg -n '^def _published_module_collection_cases_for_helper\\(|^def _published_pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    MODULE_COLLECTION_CASES,
    PATTERN_COLLECTION_CASES,
    _is_collection_type_error_fixture_case,
    _module_collection_case_from_fixture,
    _pattern_collection_case_from_fixture,
    _published_collection_fixture_cases,
)

fixture_cases = _published_collection_fixture_cases()

def module_case_ids(helper: str) -> tuple[str, ...]:
    return tuple(
        _module_collection_case_from_fixture(case).case_id
        for case in fixture_cases
        if not _is_collection_type_error_fixture_case(case)
        if case.operation == "module_call" and case.helper == helper
    )

def pattern_case_ids(helper: str) -> tuple[str, ...]:
    return tuple(
        _pattern_collection_case_from_fixture(case).case_id
        for case in fixture_cases
        if not _is_collection_type_error_fixture_case(case)
        if case.operation == "pattern_call" and case.helper == helper
    )

assert tuple(case.case_id for case in fixture_cases) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-split-str-pattern-on-bytes-string",
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-bytes-maxsplit",
    "module-findall-bytes-repeated",
    "module-findall-str-pattern-on-bytes-string",
    "pattern-findall-str-no-match",
    "pattern-findall-str-bounded",
    "pattern-findall-str-bounded-no-match",
    "pattern-findall-bytes-bounded",
    "pattern-findall-bytes-pattern-on-str-string",
    "module-finditer-str-repeated",
    "pattern-finditer-str-bounded",
    "pattern-finditer-str-bounded-no-match",
    "pattern-finditer-bytes-bounded",
    "pattern-finditer-bytes-pattern-on-str-string",
    "module-findall-nonliteral-str",
)
assert module_case_ids("split") == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
)
assert module_case_ids("findall") == (
    "module-findall-bytes-repeated",
    "module-findall-nonliteral-str",
)
assert module_case_ids("finditer") == ("module-finditer-str-repeated",)
assert pattern_case_ids("split") == (
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-bytes-maxsplit",
)
assert pattern_case_ids("findall") == (
    "pattern-findall-str-no-match",
    "pattern-findall-str-bounded",
    "pattern-findall-str-bounded-no-match",
    "pattern-findall-bytes-bounded",
)
assert pattern_case_ids("finditer") == (
    "pattern-finditer-str-bounded",
    "pattern-finditer-str-bounded-no-match",
    "pattern-finditer-bytes-bounded",
)
assert tuple(case.case_id for case in MODULE_COLLECTION_CASES) == (
    "module-split-str-leading-trailing",
    "module-split-str-no-match",
    "module-split-str-maxsplit-one",
    "module-split-str-negative-maxsplit",
    "module-split-bytes-maxsplit-one",
    "module-findall-bytes-repeated",
    "module-findall-nonliteral-str",
    "module-findall-str-repeated",
    "module-findall-str-no-match",
    "module-finditer-str-repeated",
    "module-finditer-str-no-match",
    "module-finditer-bytes-repeated",
)
assert tuple(case.case_id for case in PATTERN_COLLECTION_CASES) == (
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-bytes-maxsplit",
    "pattern-split-str-no-match",
    "pattern-split-str-repeated",
    "pattern-split-str-maxsplit-one",
    "pattern-split-str-negative-maxsplit",
    "pattern-findall-str-no-match",
    "pattern-findall-str-bounded",
    "pattern-findall-str-bounded-no-match",
    "pattern-findall-bytes-bounded",
    "pattern-findall-str-bounded",
    "pattern-findall-str-bounded-no-match",
    "pattern-findall-bytes-bounded",
    "pattern-finditer-str-bounded",
    "pattern-finditer-str-bounded-no-match",
    "pattern-finditer-bytes-bounded",
    "pattern-finditer-str-bounded",
    "pattern-finditer-str-bounded-no-match",
)
print("ok")
PY`
- `bash -lc "! rg -n '^def _published_module_collection_cases_for_helper\\(|^def _published_pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the change limited to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting duplicated selector glue over introducing another abstraction layer.
- Do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0988` is the next available task id in the current checkout:
  - `rg -n 'RBR-0988|RBR-0989|RBR-0990|RBR-0991|RBR-0992' ops/state/backlog.md ops/state/current_status.md ops/tasks` found no tracked reservation or existing task for these ids in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 10` currently ends at `RBR-0987-catch-up-pattern-split-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` currently contains only `.gitkeep`.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'` currently passes (`15 passed, 1436 deselected`);
  - the collection-helper contract probe in Verification currently passes (`ok`), confirming the live published fixture order, helper-backed module/pattern slices, and `MODULE_COLLECTION_CASES`/`PATTERN_COLLECTION_CASES` ordering already match the acceptance surface without relying on wrapper-specific behavior; and
  - `rg -n '^def _published_module_collection_cases_for_helper\\(|^def _published_pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the duplicated selector pair at lines `1098` and `1109`, so the structural no-match check will fail until this cleanup lands.
- `RBR-0893` already deleted the older top-level published collection helper-bucket mirrors in this owner file and replaced them with these two wrappers; this task is the bounded follow-on that removes the remaining module-vs-pattern selector duplication without reopening collection manifests or helper behavior.

## Completion
- Replaced `_published_module_collection_cases_for_helper(...)` and `_published_pattern_collection_cases_for_helper(...)` in `tests/python/test_module_workflow_parity_suite.py` with one shared `_published_collection_fixture_cases_for_owner(...)` selector over the existing published collection fixture rows.
- Rewired `MODULE_COLLECTION_CASES`, `PATTERN_COLLECTION_CASES`, and `test_literal_collection_direct_test_buckets_cover_selected_frontier()` to derive their published module/pattern `split`, `findall`, and `finditer` buckets from that shared selector while preserving the existing case-id ordering and direct supplemental rows.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'literal_collection_suite or literal_collection_direct_test_buckets_cover_selected_frontier or module_collection or pattern_collection or collection_type_error'` -> `15 passed, 1436 deselected`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... PY` -> `ok`
  - `bash -lc "! rg -n '^def _published_module_collection_cases_for_helper\\(|^def _published_pattern_collection_cases_for_helper\\(' tests/python/test_module_workflow_parity_suite.py"` -> success with no matches
