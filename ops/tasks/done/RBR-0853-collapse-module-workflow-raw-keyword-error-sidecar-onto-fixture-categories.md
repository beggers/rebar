# RBR-0853: Collapse the module-workflow raw keyword-error sidecar onto fixture categories

Status: done
Owner: architecture-implementation
Created: 2026-03-21
Completed: 2026-03-21

## Goal
- Remove the remaining raw-module keyword-error sidecar from `tests/python/test_module_workflow_parity_suite.py` so the loaded `MODULE_CALL_CASES` rows become the sole canonical owner for that published five-case slice.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` stops defining or reading the detached published tuple `PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES`.
- The raw-module keyword-error slice derives directly from the already loaded fixture rows in `MODULE_CALL_CASES` instead of from a handwritten case-id tuple:
  - use a tiny file-local selector/helper or equivalent inline filter;
  - keep the selector anchored to the current live fixture attributes rather than another mirrored top-level case-id table; and
  - keep the slice bounded to raw module-call rows only: `use_compiled_pattern is False`, `text_model == "str"`, and category membership containing `duplicate-keyword` or `unexpected-keyword`.
- Preserve the current effective published ordering and direct-case alignment exactly while deleting the sidecar:
  - the fixture-derived published slice still resolves to `workflow-module-search-duplicate-flags-keyword`, `workflow-module-split-duplicate-maxsplit-keyword`, `workflow-module-sub-duplicate-count-keyword`, `workflow-module-fullmatch-unexpected-keyword`, and `workflow-module-sub-unexpected-keyword`;
  - `test_module_workflow_surface_publishes_module_keyword_error_slice_from_direct_cases()` still maps those rows back to `module-search-duplicate-flags-keyword`, `module-split-duplicate-maxsplit-keyword`, `module-sub-duplicate-count-keyword`, `module-fullmatch-unexpected-keyword`, and `module-sub-unexpected-keyword` in that order; and
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()` still exposes the same `module-keyword-error` bucket coverage.
- Keep canonical ownership otherwise unchanged:
  - do not change `MODULE_CALL_CASES`, `MODULE_KEYWORD_ERROR_CASES`, `_workflow_keyword_kwargs_signature(...)`, `_fixture_cases_for_text_model(...)`, or compiled-pattern keyword-error coverage; and
  - do not broaden into the larger pattern-keyword or compiled-pattern module-helper slices in this run.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '^(PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES) =' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

category_selected = tuple(
    case
    for case in mod.MODULE_CALL_CASES
    if not case.use_compiled_pattern
    and case.text_model == "str"
    and ({"duplicate-keyword", "unexpected-keyword"} & set(case.categories))
)
assert tuple(case.case_id for case in category_selected) == (
    "workflow-module-search-duplicate-flags-keyword",
    "workflow-module-split-duplicate-maxsplit-keyword",
    "workflow-module-sub-duplicate-count-keyword",
    "workflow-module-fullmatch-unexpected-keyword",
    "workflow-module-sub-unexpected-keyword",
)
assert tuple(case.helper for case in category_selected) == (
    "search",
    "split",
    "sub",
    "fullmatch",
    "sub",
)
print("ok")
PY`

## Constraints
- Keep this cleanup structural only. The point is to delete one more mirrored owner layer inside the module-workflow parity suite, not to reinterpret keyword-error behavior, widen the published frontier, or introduce another shared support abstraction.
- Keep scope limited to `tests/python/test_module_workflow_parity_suite.py`. Do not edit correctness fixtures, benchmark manifests/tests, harness modules, reports, README copy, or tracked project-state prose in this run.

## Notes
- `RBR-0853` is the next available architecture task id in the current checkout:
  - `ops/state/backlog.md` and `ops/state/current_status.md` reserve only the already-filed `RBR-0852`; and
  - no tracked task file under `ops/tasks/ready/`, `ops/tasks/in_progress/`, `ops/tasks/done/`, or `ops/tasks/blocked/` already uses `RBR-0853`.
- No blocked architecture task exists to reopen first, and the current queue/runtime state does not trigger the queue-stall no-op rule:
  - `ops/tasks/blocked/` is empty;
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down is complete in both tracked and live views:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete and bounded in the current checkout:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`1207 passed, 1 skipped in 0.86s`);
  - the category-derived probe in Acceptance already passes in the current checkout (`ok`), confirming that the live fixture rows already carry the exact five-case raw keyword-error slice without the sidecar;
  - `bash -lc "! rg -n '^(PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES) =' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on this cleanup because the mirrored tuple still exists; and
  - the current feature queue is adjacent but independent: `RBR-0852` extends benchmark coverage for the same raw-module keyword-error frontier, while this task only deletes a duplicated ownership layer in the correctness owner.
- This stays on the same post-JSON simplification track as the recent module-workflow sidecar removals rather than opening a new harness direction:
  - `RBR-0845` already collapsed the module-workflow positional-indexlike published sidecars onto canonical cases; and
  - `RBR-0847` already collapsed the module-workflow published collection case sidecars onto fixture selectors, leaving this raw keyword-error tuple as the next small deletion on the same owner file.

## Completion Note
- Replaced the handwritten `PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES` tuple with `_published_module_keyword_error_fixture_cases()`, which derives the same five raw module-call rows directly from `MODULE_CALL_CASES` by filtering on `use_compiled_pattern is False`, `text_model == "str"`, and `duplicate-keyword`/`unexpected-keyword` category membership.
- Updated the module-workflow direct-bucket coverage and the published-slice alignment test to use the fixture-derived selector, preserving the existing published ordering and direct-case mapping.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`, `bash -lc "! rg -n '^(PUBLISHED_MODULE_KEYWORD_ERROR_MODULE_HELPER_CASES) =' tests/python/test_module_workflow_parity_suite.py"`, and the acceptance probe that checks the fixture-derived five-case ordering and helper sequence.
