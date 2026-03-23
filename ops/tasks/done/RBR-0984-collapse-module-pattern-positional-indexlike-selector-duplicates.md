# RBR-0984: Collapse module/pattern positional-indexlike selector duplicates

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the duplicated module-vs-pattern positional-`__index__` selector pairings from `tests/python/test_module_workflow_parity_suite.py` so the module and pattern publication slices flow through one smaller file-local selector surface instead of keeping two near-identical signature/fixture helper stacks.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines the duplicated positional-indexlike selector helpers:
  - `_module_positional_indexlike_direct_signature(...)`
  - `_published_module_positional_indexlike_fixture_cases(...)`
  - `_pattern_positional_indexlike_direct_signature(...)`
  - `_published_pattern_positional_indexlike_fixture_cases(...)`
- Replace that duplicated stack with one explicit but smaller shared helper surface that is parameterized by the direct-call collections and fixture-case collections already present in the file:
  - `test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases()` derives its published fixture rows and aligned direct cases from the shared helper surface instead of the module-specific helper pair; and
  - `test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases()` derives its published fixture rows and aligned direct cases from the same shared helper surface instead of the pattern-specific helper pair.
- Preserve the current live publication contracts exactly while removing the duplicate selector stack:
  - the module positional-indexlike slice still resolves to `3` published fixture rows and `3` selected direct rows;
  - the module `str` split still stays `("workflow-module-sub-count-indexlike-positional-str",)`;
  - the module `bytes` split still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module published fixture order still stays `("workflow-module-split-maxsplit-indexlike-positional-bytes", "workflow-module-sub-count-indexlike-positional-str", "workflow-module-subn-count-indexlike-positional-bytes")`;
  - the module selected direct-case order still stays `("module-split-maxsplit-indexlike-positional-bytes", "module-sub-count-indexlike-positional-str", "module-subn-count-indexlike-positional-bytes")`;
  - the module helper split still stays `Counter({"split": 1, "sub": 1, "subn": 1})`;
  - the pattern positional-indexlike slice still resolves to `9` published fixture rows and `9` selected direct rows;
  - the pattern `str` split still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-subn-count-indexlike-positional-str")`;
  - the pattern `bytes` split still stays `("workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes")`;
  - the pattern published fixture order still stays `("workflow-pattern-search-str-pos-indexlike-positional", "workflow-pattern-search-bytes-endpos-indexlike-positional", "workflow-pattern-match-bytes-window-indexlike-positional", "workflow-pattern-fullmatch-bytes-window-indexlike-positional", "workflow-pattern-findall-str-window-indexlike-positional", "workflow-pattern-finditer-bytes-window-indexlike-positional", "workflow-pattern-split-str-maxsplit-indexlike-positional", "workflow-pattern-sub-count-indexlike-positional-bytes", "workflow-pattern-subn-count-indexlike-positional-str")`;
  - the pattern selected direct-case order still stays `("pattern-search-pos-indexlike-positional-str", "pattern-search-endpos-indexlike-positional-bytes", "pattern-match-window-indexlike-positional-bytes", "pattern-fullmatch-window-indexlike-positional-bytes", "pattern-findall-window-indexlike-positional-str", "pattern-finditer-window-indexlike-positional-bytes", "pattern-split-maxsplit-indexlike-positional-str", "pattern-sub-count-indexlike-positional-bytes", "pattern-subn-count-indexlike-positional-str")`; and
  - the pattern helper split still stays `Counter({"search": 2, "match": 1, "fullmatch": 1, "findall": 1, "finditer": 1, "split": 1, "sub": 1, "subn": 1})`.
- Keep the cleanup structural and file-local:
  - keep `MODULE_POSITIONAL_INDEXLIKE_CALL_CASES`, `PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES`, `_workflow_positional_indexlike_fixture_signature(...)`, `_fixture_cases_for_text_model(...)`, and the existing direct/publication tests as the canonical live surfaces unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this task into owner-path row helpers, compiled-pattern module-helper publication, numeric-coercion behavior, fixture manifests, benchmark files, harness modules, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.
- The structural simplification is visible in the file:
  - `rg -n '^def _module_positional_indexlike_direct_signature\\(|^def _published_module_positional_indexlike_fixture_cases\\(|^def _pattern_positional_indexlike_direct_signature\\(|^def _published_pattern_positional_indexlike_fixture_cases\\(' tests/python/test_module_workflow_parity_suite.py` returns no matches.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_POSITIONAL_INDEXLIKE_CALL_CASES,
    PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES,
    _fixture_cases_for_text_model,
    _module_positional_indexlike_direct_signature,
    _pattern_positional_indexlike_direct_signature,
    _published_module_positional_indexlike_fixture_cases,
    _published_pattern_positional_indexlike_fixture_cases,
    _workflow_positional_indexlike_fixture_signature,
)

module_published = _published_module_positional_indexlike_fixture_cases()
module_direct_by_signature = {
    _module_positional_indexlike_direct_signature(case): case
    for case in MODULE_POSITIONAL_INDEXLIKE_CALL_CASES
}
module_selected = tuple(
    module_direct_by_signature[_workflow_positional_indexlike_fixture_signature(case)]
    for case in module_published
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(module_published, "str")) == (
    "workflow-module-sub-count-indexlike-positional-str",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(module_published, "bytes")) == (
    "workflow-module-split-maxsplit-indexlike-positional-bytes",
    "workflow-module-subn-count-indexlike-positional-bytes",
)
assert tuple(case.case_id for case in module_published) == (
    "workflow-module-split-maxsplit-indexlike-positional-bytes",
    "workflow-module-sub-count-indexlike-positional-str",
    "workflow-module-subn-count-indexlike-positional-bytes",
)
assert tuple(case.case_id for case in module_selected) == (
    "module-split-maxsplit-indexlike-positional-bytes",
    "module-sub-count-indexlike-positional-str",
    "module-subn-count-indexlike-positional-bytes",
)
assert Counter(case.helper for case in module_published) == Counter({"split": 1, "sub": 1, "subn": 1})

pattern_published = _published_pattern_positional_indexlike_fixture_cases()
pattern_direct_by_signature = {
    _pattern_positional_indexlike_direct_signature(case): case
    for case in PATTERN_POSITIONAL_INDEXLIKE_CALL_CASES
}
pattern_selected = tuple(
    pattern_direct_by_signature[_workflow_positional_indexlike_fixture_signature(case)]
    for case in pattern_published
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(pattern_published, "str")) == (
    "workflow-pattern-search-str-pos-indexlike-positional",
    "workflow-pattern-findall-str-window-indexlike-positional",
    "workflow-pattern-split-str-maxsplit-indexlike-positional",
    "workflow-pattern-subn-count-indexlike-positional-str",
)
assert tuple(case.case_id for case in _fixture_cases_for_text_model(pattern_published, "bytes")) == (
    "workflow-pattern-search-bytes-endpos-indexlike-positional",
    "workflow-pattern-match-bytes-window-indexlike-positional",
    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
    "workflow-pattern-finditer-bytes-window-indexlike-positional",
    "workflow-pattern-sub-count-indexlike-positional-bytes",
)
assert tuple(case.case_id for case in pattern_published) == (
    "workflow-pattern-search-str-pos-indexlike-positional",
    "workflow-pattern-search-bytes-endpos-indexlike-positional",
    "workflow-pattern-match-bytes-window-indexlike-positional",
    "workflow-pattern-fullmatch-bytes-window-indexlike-positional",
    "workflow-pattern-findall-str-window-indexlike-positional",
    "workflow-pattern-finditer-bytes-window-indexlike-positional",
    "workflow-pattern-split-str-maxsplit-indexlike-positional",
    "workflow-pattern-sub-count-indexlike-positional-bytes",
    "workflow-pattern-subn-count-indexlike-positional-str",
)
assert tuple(case.case_id for case in pattern_selected) == (
    "pattern-search-pos-indexlike-positional-str",
    "pattern-search-endpos-indexlike-positional-bytes",
    "pattern-match-window-indexlike-positional-bytes",
    "pattern-fullmatch-window-indexlike-positional-bytes",
    "pattern-findall-window-indexlike-positional-str",
    "pattern-finditer-window-indexlike-positional-bytes",
    "pattern-split-maxsplit-indexlike-positional-str",
    "pattern-sub-count-indexlike-positional-bytes",
    "pattern-subn-count-indexlike-positional-str",
)
assert Counter(case.helper for case in pattern_published) == Counter(
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
)
print("ok")
PY`
- `bash -lc "! rg -n '^def _module_positional_indexlike_direct_signature\\(|^def _published_module_positional_indexlike_fixture_cases\\(|^def _pattern_positional_indexlike_direct_signature\\(|^def _published_pattern_positional_indexlike_fixture_cases\\(' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting duplicated selector glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0984` is the next available task id in the current checkout:
  - `rg -n 'RBR-0984|RBR-0985|RBR-0986|RBR-0987|RBR-0988' ops/state/backlog.md ops/state/current_status.md` returned no matches in this run; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 20` currently ends at `RBR-0983-catch-up-pattern-finditer-bounded-trio.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'` currently passes (`2 passed, 1445 deselected`);
  - the positional-indexlike contract probe in Verification currently passes (`ok`), confirming that the live module and pattern publication slices already preserve their current fixture ordering, text-model splits, direct-case ordering, and helper splits;
  - `rg -n '^def _module_positional_indexlike_direct_signature\\(|^def _published_module_positional_indexlike_fixture_cases\\(|^def _pattern_positional_indexlike_direct_signature\\(|^def _published_pattern_positional_indexlike_fixture_cases\\(' tests/python/test_module_workflow_parity_suite.py` currently finds the duplicated selector stack at lines `2423`, `2446`, `2783`, and `2794`, so the structural no-match check will fail until this cleanup lands; and
  - `RBR-0845` already collapsed the detached positional-indexlike published sidecars onto canonical owners, so this follow-on can stay narrowly focused on the still-live selector duplication instead of reopening removed sidecar state.

## Completion
- Replaced the duplicated module/pattern positional-`__index__` selector helpers in `tests/python/test_module_workflow_parity_suite.py` with one shared direct-signature helper plus shared published-fixture/direct-case selectors.
- Repointed the module and pattern positional-indexlike publication tests, along with the selected-frontier bucket coverage check, to the shared helper surface without changing the published row counts, ordering, text-model splits, or helper counts.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'test_module_workflow_surface_publishes_module_positional_indexlike_slice_from_direct_cases or test_module_workflow_surface_publishes_pattern_positional_indexlike_slice_from_direct_cases'`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY' ... shared positional-indexlike contract probe ... PY`
  - `bash -lc "! rg -n '^def _module_positional_indexlike_direct_signature\\(|^def _published_module_positional_indexlike_fixture_cases\\(|^def _pattern_positional_indexlike_direct_signature\\(|^def _published_pattern_positional_indexlike_fixture_cases\\(' tests/python/test_module_workflow_parity_suite.py"`
