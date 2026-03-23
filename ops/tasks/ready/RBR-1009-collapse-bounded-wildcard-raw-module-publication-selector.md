## RBR-1009: Collapse bounded wildcard raw module publication selector

Status: ready
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining bespoke bounded-wildcard raw-module publication selector from `tests/python/test_module_workflow_parity_suite.py` so that this three-row noncompiled module slice uses the same owner-path publication machinery already used by the neighboring module/pattern publication tests instead of maintaining its own fixture-filter and signature-matching path.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` replaces the dedicated `_published_bounded_wildcard_raw_module_helper_fixture_cases()` path with one owner-path-based publication contract surface, or a strictly smaller equivalent, for the raw bounded-wildcard module helper slice built from the exact published/direct pairs:
  - `workflow-module-search-str-bounded-wildcard-ignorecase` -> `module-search-ignorecase-bounded-hit`
  - `workflow-module-match-str-bounded-wildcard-miss` -> `module-match-bounded-miss`
  - `workflow-module-fullmatch-str-bounded-wildcard` -> `module-fullmatch-bounded-hit`
- Repoint both existing bounded-wildcard raw-module consumers through that shared owner-path-based path instead of leaving either one to read the bespoke selector:
  - `test_module_workflow_direct_test_buckets_cover_selected_frontier()`
  - `test_module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases()`
- Preserve the current bounded-wildcard raw-module publication contract exactly while deleting the custom selector plumbing:
  - the published fixture-case order still resolves to:
    - `workflow-module-search-str-bounded-wildcard-ignorecase`
    - `workflow-module-match-str-bounded-wildcard-miss`
    - `workflow-module-fullmatch-str-bounded-wildcard`
  - the selected direct-case order still resolves to:
    - `module-search-ignorecase-bounded-hit`
    - `module-match-bounded-miss`
    - `module-fullmatch-bounded-hit`
  - the helper counts still resolve to `Counter({"search": 1, "match": 1, "fullmatch": 1})`;
  - the slice still stays entirely `str`-mode and noncompiled;
  - fixture helpers still align one-for-one with the selected direct-case helpers; and
  - each selected pair still proves the same field-level contract as today: `case_pattern(fixture_case) == direct_case.pattern`, `tuple(fixture_case.args) == (direct_case.string,)`, and `fixture_case.flags == direct_case.flags`.
- Prefer deletion over another detached abstraction layer:
  - remove `_published_bounded_wildcard_raw_module_helper_fixture_cases()` if the shared owner-path path leaves it unused;
  - keep the cleanup local to `tests/python/test_module_workflow_parity_suite.py`;
  - do not widen this run into compiled bounded-wildcard helper publication, bounded-wildcard CPython behavior tests, benchmark files, harness modules, reports, or tracked state prose; and
  - do not add a new shared helper module, registry outside this file, or checked-in data representation outside the ordinary file-local owner-path structures already used in this suite.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases'`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer moving this slice onto the existing owner-path publication contract helpers over introducing a new parallel selector/helper stack.
- Do not edit fixture manifests, harness modules, benchmark workloads/tests, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-1009` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-1009|RBR-1010|RBR-1011|RBR-1012' ops/state/backlog.md ops/state/current_status.md ops/tasks/ready ops/tasks/in_progress ops/tasks/blocked -g '*.md'` returned no matches in the current checkout.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, and `blocked: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The simplification target is concrete in the live checkout:
  - `tests/python/test_module_workflow_parity_suite.py` still defines `_published_bounded_wildcard_raw_module_helper_fixture_cases()` at line `317`;
  - the direct-test bucket coverage test still reads that bespoke selector at line `4312`; and
  - the raw bounded-wildcard publication test still rebuilds its own fixture/direct-case selection around lines `4722`-`4767` instead of using the shared owner-path publication contract helpers already used by the neighboring module/pattern publication slices.
- The verification slice is green before the cleanup:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_workflow_direct_test_buckets_cover_selected_frontier or module_workflow_surface_publishes_bounded_wildcard_raw_module_helpers_from_direct_cases'` currently passes with `2 passed, 1449 deselected`.
