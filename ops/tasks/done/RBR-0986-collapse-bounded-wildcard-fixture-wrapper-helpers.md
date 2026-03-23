# RBR-0986: Collapse bounded wildcard fixture wrapper helpers

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining bounded-wildcard fixture wrapper helpers from `tests/python/test_module_workflow_parity_suite.py` so the bounded-wildcard publication and parametrization paths use the existing generic `_published_bounded_wildcard_fixture_cases(...)` selector directly instead of carrying three fixed wrappers over the same file-local helper surface.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines the three bounded-wildcard wrapper helpers:
  - `_published_bounded_wildcard_compile_fixture_cases(...)`
  - `_published_bounded_wildcard_pattern_fixture_cases(...)`
  - `_published_bounded_wildcard_pattern_fixture_cases_for_helpers(...)`
- Replace those wrappers with direct use of the existing generic bounded-wildcard selector at the live call sites:
  - `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases()` derives `bounded_wildcard_pattern_case_ids`, `bounded_wildcard_compile_cases`, and `bounded_wildcard_pattern_cases` from `_published_bounded_wildcard_fixture_cases(...)` with `PATTERN_CASES` or `COMPILE_CASES` instead of the removed wrappers;
  - `test_bounded_wildcard_compile_metadata_matches_cpython()`, `test_bounded_wildcard_generated_module_match_matrix_matches_cpython()`, and `test_bounded_wildcard_generated_pattern_match_matrix_with_windows_matches_cpython()` parametrize directly from `_published_bounded_wildcard_fixture_cases(COMPILE_CASES)`; and
  - `test_bounded_wildcard_pattern_match_helpers_match_cpython()` and `test_bounded_wildcard_pattern_collection_helpers_match_cpython()` derive their helper-specific pattern subsets by filtering `_published_bounded_wildcard_fixture_cases(PATTERN_CASES)` directly instead of routing through a second wrapper.
- Preserve the current bounded-wildcard publication contracts exactly while deleting the wrappers:
  - the bounded-wildcard compile slice still resolves to `2` published fixture rows, both `str`, in this order:
    - `workflow-compile-str-bounded-wildcard`
    - `workflow-compile-str-bounded-wildcard-ignorecase`
  - the compile slice still preserves this `(case_id, pattern, flags)` signature order:
    - `("workflow-compile-str-bounded-wildcard", "a.c", 0)`
    - `("workflow-compile-str-bounded-wildcard-ignorecase", "a.c", 2)`
  - the bounded-wildcard pattern slice still resolves to `6` published fixture rows, all `str`, in this order:
    - `workflow-pattern-search-str-bounded-wildcard-ignorecase`
    - `workflow-pattern-match-str-bounded-wildcard`
    - `workflow-pattern-fullmatch-str-bounded-wildcard`
    - `workflow-pattern-findall-str-bounded-wildcard`
    - `workflow-pattern-finditer-str-bounded-wildcard`
    - `workflow-pattern-search-str-bounded-wildcard-endpos-miss`
  - the bounded-wildcard pattern match-helper subset still resolves to these `4` rows in order:
    - `workflow-pattern-search-str-bounded-wildcard-ignorecase`
    - `workflow-pattern-match-str-bounded-wildcard`
    - `workflow-pattern-fullmatch-str-bounded-wildcard`
    - `workflow-pattern-search-str-bounded-wildcard-endpos-miss`
  - the bounded-wildcard pattern collection-helper subset still resolves to these `2` rows in order:
    - `workflow-pattern-findall-str-bounded-wildcard`
    - `workflow-pattern-finditer-str-bounded-wildcard`
- Keep the cleanup structural and file-local:
  - keep `_published_bounded_wildcard_fixture_cases(...)` as the canonical file-local selector unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into collection-helper selectors, owner-path selectors, positional-indexlike selectors, compiled-pattern module-helper owner paths, manifests, harness modules, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.
- The structural simplification is visible in the file:
  - `rg -n '^def _published_bounded_wildcard_compile_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases_for_helpers\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard_compile_metadata_matches_cpython or bounded_wildcard_pattern_match_helpers_match_cpython or bounded_wildcard_pattern_collection_helpers_match_cpython or module_workflow_surface_bundle_contract_covers_regression_compile_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    COMPILE_CASES,
    PATTERN_CASES,
    _published_bounded_wildcard_fixture_cases,
)

compile_cases = _published_bounded_wildcard_fixture_cases(COMPILE_CASES)
pattern_cases = _published_bounded_wildcard_fixture_cases(PATTERN_CASES)
match_cases = tuple(
    case
    for case in pattern_cases
    if case.helper in {"search", "match", "fullmatch"}
)
collection_cases = tuple(
    case
    for case in pattern_cases
    if case.helper in {"findall", "finditer"}
)

assert tuple(case.case_id for case in compile_cases) == (
    "workflow-compile-str-bounded-wildcard",
    "workflow-compile-str-bounded-wildcard-ignorecase",
)
assert tuple(
    (case.case_id, case.pattern, case.flags or 0)
    for case in compile_cases
) == (
    ("workflow-compile-str-bounded-wildcard", "a.c", 0),
    ("workflow-compile-str-bounded-wildcard-ignorecase", "a.c", 2),
)
assert tuple(case.case_id for case in pattern_cases) == (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)
assert tuple(case.case_id for case in match_cases) == (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)
assert tuple(case.case_id for case in collection_cases) == (
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
)
print("ok")
PY`
- `bash -lc "! rg -n '^def _published_bounded_wildcard_compile_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases_for_helpers\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting fixed wrapper glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0986` is the next available task id in the current checkout:
  - `rg -n 'RBR-0986|RBR-0987|RBR-0988|RBR-0989|RBR-0990' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0985-publish-pattern-split-str-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The bounded-wildcard wrapper target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard_compile_metadata_matches_cpython or bounded_wildcard_pattern_match_helpers_match_cpython or bounded_wildcard_pattern_collection_helpers_match_cpython or module_workflow_surface_bundle_contract_covers_regression_compile_cases'` currently passes (`17 passed, 1434 deselected`);
  - the generic bounded-wildcard probe in Verification currently passes (`ok`), confirming that `_published_bounded_wildcard_fixture_cases(COMPILE_CASES)` and `_published_bounded_wildcard_fixture_cases(PATTERN_CASES)` already preserve the live compile slice, full pattern slice, match-helper subset, and collection-helper subset without relying on wrapper-specific behavior; and
  - `rg -n '^def _published_bounded_wildcard_compile_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases\\(|^def _published_bounded_wildcard_pattern_fixture_cases_for_helpers\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the wrapper definitions at lines `314`, `318`, and `322`, so the structural no-match check will fail until this cleanup lands.

## Completion
- Removed the three bounded-wildcard wrapper helpers from `tests/python/test_module_workflow_parity_suite.py` and switched the affected contract assertions and parametrized tests to call `_published_bounded_wildcard_fixture_cases(...)` directly, with inline helper filtering for the pattern helper subsets.
- Verified with the targeted pytest slice (`17 passed, 1434 deselected`), the direct selector-order probe (`ok`), and the structural `rg` no-match check.
