# RBR-1023: Collapse verbose regression case-id maps onto canonical tuples

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining verbose-regression case-id lookup maps from `tests/python/test_module_workflow_parity_suite.py` so the verbose pattern regression checks and verbose compiled-pattern helper rows derive from the same canonical file-local case tuples instead of routing through detached `*_BY_ID` dictionaries.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads:
  - `PATTERN_CASES_BY_ID`; and
  - the local `verbose_cases_by_id` map inside `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases()`.
- Replace those detached lookups with one smaller file-local route, or a strictly smaller equivalent, that keeps the verbose regression slice anchored on the existing canonical tuples:
  - `PATTERN_CASES`;
  - `VERBOSE_COMPILE_WORKFLOW_CASES`; and
  - `VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES` / `COMPILED_PATTERN_MODULE_HELPER_CASES`.
- Preserve the current verbose compiled-pattern helper contract exactly while shrinking the representation:
  - `VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES` still resolves, in order, to:
    - `compiled-pattern-search-bytes-verbose-regression`
    - `compiled-pattern-fullmatch-bytes-verbose-regression`
  - those rows still carry the same `pattern`, `args`, and `flags` currently sourced from the published bytes verbose pattern cases; and
  - `COMPILED_PATTERN_MODULE_HELPER_CASES[3:5]` still resolves to those same two verbose compiled-pattern helper rows in the same order.
- Preserve the current verbose fixture/regression coverage in `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases()`:
  - the test still proves the same published verbose `PATTERN_CASES` rows align with the same `VERBOSE_COMPILE_WORKFLOW_CASES` cases for the `search` and `fullmatch` str/bytes slices;
  - the bytes verbose pattern rows still share `case_pattern(...) == case_pattern(VERBOSE_BYTES_COMPILE_CASE)` and `flags == VERBOSE_BYTES_COMPILE_CASE.flags`; and
  - the current str/bytes argument expectations for the six verbose search/fullmatch follow-on rows stay unchanged.
- Keep the cleanup structural and file-local:
  - prefer one filtered tuple, paired tuple, or equivalent file-local helper over another case-id map, registry, or helper module;
  - keep the cleanup inside `tests/python/test_module_workflow_parity_suite.py` instead of widening into harness modules, fixture manifests, benchmark files, reports, or tracked state prose; and
  - do not widen this run into verbose execution behavior changes, bounded-wildcard cleanup, owner-path publication cleanup outside the verbose slice, or CPython behavior changes.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_bundle_contract_covers_regression_compile_cases or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or verbose'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.test_module_workflow_parity_suite import (
    COMPILED_PATTERN_MODULE_HELPER_CASES,
    VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES,
)

assert tuple(case.case_id for case in VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES) == (
    "compiled-pattern-search-bytes-verbose-regression",
    "compiled-pattern-fullmatch-bytes-verbose-regression",
)
assert tuple(case.case_id for case in COMPILED_PATTERN_MODULE_HELPER_CASES[3:5]) == (
    "compiled-pattern-search-bytes-verbose-regression",
    "compiled-pattern-fullmatch-bytes-verbose-regression",
)
print("ok")
PY`
- `bash -lc "! rg -n '^PATTERN_CASES_BY_ID = |verbose_cases_by_id = ' tests/python/test_module_workflow_parity_suite.py"`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting the verbose case-id maps over introducing another detached selector or registry.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, or tracked state prose in this run.

## Notes
- `RBR-1023` is the next available unreserved task id in the current checkout:
  - a current-run scan across `ops/state/current_status.md`, `ops/state/backlog.md`, and `ops/tasks/**` reported `next_id=1023`, `max_seen=1022`, and no reserved `RBR-1023` reference.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in this checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, and both task workers finished `done` in the last recorded cycle.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `.rebar/runtime/loop_state.json` reports `tracked_json_blob_count: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines the global `PATTERN_CASES_BY_ID` map and the local `verbose_cases_by_id` map;
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_surface_bundle_contract_covers_regression_compile_cases or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases or verbose'` currently passes (`103 passed, 1348 deselected`);
  - the inline helper probe in Verification currently reports `ok`; and
  - `bash -lc "rg -n '^PATTERN_CASES_BY_ID = |verbose_cases_by_id = ' tests/python/test_module_workflow_parity_suite.py"` currently finds both detached maps, so the final `! rg ...` acceptance check will fail only on the cleanup being queued here.
