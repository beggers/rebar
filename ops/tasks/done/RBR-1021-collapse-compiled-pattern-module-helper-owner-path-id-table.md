# RBR-1021: Collapse compiled-pattern module-helper owner-path id table

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining `direct_case_id` lookup table behavior from `tests/python/test_module_workflow_parity_suite.py` so the compiled-pattern module-helper owner path carries direct-case objects from the canonical file-local case tuples instead of routing through a detached string-id resolver across six collections.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads `CompiledPatternModuleHelperOwnerPathRow.direct_case_id`.
- Replace the current property-based direct-case lookup with direct-case ownership on the row objects themselves:
  - prefer one or a few ordered fixture-id tuples zipped against canonical case slices or concatenations from the existing file-local case families;
  - keep the cleanup inside `tests/python/test_module_workflow_parity_suite.py` instead of adding a new helper module, registry, or support layer; and
  - keep `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS` as the canonical owner-path surface for the compiled-pattern module-helper publication tests.
- Preserve the current compiled-pattern module-helper publication contract exactly:
  - `_assert_compiled_pattern_module_helper_publication_contract()` stays green with `expected_count=62`, text-model counts `Counter({"str": 33, "bytes": 29})`, and helper counts `Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10})`;
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()` stays green on the same owner path; and
  - `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()` keeps the same six-row fixture order and the same adjacent `direct_case.case_id` sequence:
    - `compiled-pattern-sub-unexpected-keyword-str`
    - `compiled-pattern-sub-unexpected-keyword-after-positional-count-str`
    - `compiled-pattern-sub-count-alias-keyword-str`
    - `compiled-pattern-subn-unexpected-keyword-bytes`
    - `compiled-pattern-subn-unexpected-keyword-after-positional-count-bytes`
    - `compiled-pattern-subn-count-alias-keyword-bytes`
- Keep the representation smaller than the current detached id table:
  - do not replace `direct_case_id` with another case-id map, another string-key registry, or another cross-collection resolver; and
  - prefer direct-case row construction over the current 62-entry handwritten `CompiledPatternModuleHelperOwnerPathRow(... direct_case_id=...)` block when a compact file-local zip or equivalent preserves the same order.
- Keep the cleanup structural and local:
  - do not edit fixture manifests, harness modules, benchmark files, reports, README/current-status/backlog prose, or non-parity test files; and
  - do not widen this run into raw-module owner-path cleanup, compiled-pattern keyword bool-count complements, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
)

assert len(COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS) == 62
assert not hasattr(COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS[0], "direct_case_id")
assert COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS[0].fixture_case_id == (
    "workflow-module-compile-str-compiled-pattern"
)
assert COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS[0].direct_case.case_id == (
    "compiled-pattern-compile-str-literal"
)
assert COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS[-1].fixture_case_id == (
    "workflow-module-subn-bytes-compiled-pattern-on-str-string"
)
assert COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS[-1].direct_case.case_id == (
    "compiled-pattern-subn-bytes-on-str-string"
)
print("ok")
PY`
- `bash -lc "! rg -n '\\bdirect_case_id\\b' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the detached id resolver over introducing another owner-path registry.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- `RBR-1021` is the next available unreserved task id in the current checkout:
  - a current-run scan across `ops/state/current_status.md`, `ops/state/backlog.md`, and `ops/tasks/**` found no existing `RBR-1021` reference.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` contains only `.gitkeep` in this checkout.
- JSON burn-down remains complete, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/loop_state.json` is lagging those fields (`tracked_json_blob_delta` is `null`), but the live checkout matches the dashboard `HEAD`;
  - `git rev-parse HEAD` returned `744da0c815e0e38445e8cd070b75e64c429d30c2`, matching the dashboard `HEAD`;
  - `git status --short` was empty in this run;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The cleanup target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `CompiledPatternModuleHelperOwnerPathRow.direct_case_id` and a 62-entry `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS` block built from those ids;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path'` currently passes (`2 passed, 1449 deselected`);
  - the inline owner-path probe in Verification currently fails exactly because the rows still expose `direct_case_id`; and
  - `bash -lc "! rg -n '\\bdirect_case_id\\b' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on the detached id-table cleanup being queued here.

## Completion
- Replaced `CompiledPatternModuleHelperOwnerPathRow.direct_case_id` with direct-case ownership and rebuilt `COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS` from ordered fixture-id tuples zipped against file-local case slices and concatenations.
- Verified the targeted publication tests still pass, the owner-path probe reports `ok`, and `rg` finds no remaining `direct_case_id` references in `tests/python/test_module_workflow_parity_suite.py`.
