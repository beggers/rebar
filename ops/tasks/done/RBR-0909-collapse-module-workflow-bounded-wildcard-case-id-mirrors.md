# RBR-0909: Collapse module-workflow bounded-wildcard case-id mirrors

Status: done
Owner: architecture-implementation
Created: 2026-03-22
Completed: 2026-03-22

## Goal
- Remove the detached `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS` and `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS` tuples from `tests/python/test_module_workflow_parity_suite.py`, so the bounded-wildcard compile and pattern subsets derive directly from the canonical `module-workflow-surface` bundle rows the owner file already loads instead of maintaining two handwritten case-id mirrors.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` no longer defines or reads `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS` or `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS`:
  - delete both top-level tuples instead of replacing them with another detached tuple/list/set/map; and
  - if a helper remains, keep it as one tiny file-local live selector over the loaded bounded-wildcard fixture rows rather than another cached selector mirror.
- Route the bounded-wildcard compile and pattern subsets through live owner data instead of the deleted case-id mirrors:
  - `_published_bounded_wildcard_compile_fixture_cases()` derives its two-row subset from the live module-workflow compile rows rather than from case-id lookups;
  - `_published_bounded_wildcard_pattern_fixture_cases()` derives its six-row subset from the live module-workflow pattern rows rather than from case-id lookups;
  - preserve the current ordered compile subset exactly as `workflow-compile-str-bounded-wildcard`, then `workflow-compile-str-bounded-wildcard-ignorecase`;
  - preserve the current ordered pattern subset exactly as `workflow-pattern-search-str-bounded-wildcard-ignorecase`, `workflow-pattern-match-str-bounded-wildcard`, `workflow-pattern-fullmatch-str-bounded-wildcard`, `workflow-pattern-findall-str-bounded-wildcard`, `workflow-pattern-finditer-str-bounded-wildcard`, then `workflow-pattern-search-str-bounded-wildcard-endpos-miss`; and
  - use structural fixture properties already present on the loaded rows for the live selection path instead of introducing new case-id mirrors or another registry table.
- Rewire the current owner-path checks through those live selectors instead of the deleted tuples:
  - `test_module_workflow_surface_bundle_contract_covers_regression_compile_cases()`;
  - `_published_bounded_wildcard_pattern_match_fixture_cases()` and `_published_bounded_wildcard_pattern_collection_fixture_cases()` if they still read the pattern subset helper; and
  - any other reads of the removed case-id tuples in `tests/python/test_module_workflow_parity_suite.py`.
- Keep this cleanup structural only:
  - do not change fixture contents, direct bounded-wildcard cases, compiled-pattern helper coverage, keyword or positional-indexlike parity coverage, collection/replacement owner paths, benchmark/report outputs, or tracked project-state prose; and
  - do not widen into a general module-workflow helper refactor, fixture rewrites, or harness-module edits in this run.
- Verification passes with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '^MODULE_WORKFLOW_BOUNDED_WILDCARD_(COMPILE|PATTERN)_CASE_IDS = ' tests/python/test_module_workflow_parity_suite.py"`
  - `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from tests.python.fixture_parity_support import case_pattern, load_published_fixture_bundles, published_fixture_bundles_by_manifest_id
from rebar_harness.correctness import MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR, select_correctness_fixture_paths

bundles = load_published_fixture_bundles(
    select_correctness_fixture_paths(MODULE_WORKFLOW_SURFACE_FIXTURE_SELECTOR)
)
module_bundle = published_fixture_bundles_by_manifest_id(bundles)["module-workflow-surface"]
compile_case_ids = tuple(
    case.case_id
    for case in module_bundle.cases
    if case.operation == "compile"
    and case.text_model == "str"
    and case_pattern(case) == "a.c"
)
pattern_case_ids = tuple(
    case.case_id
    for case in module_bundle.cases
    if case.operation == "pattern_call"
    and case.text_model == "str"
    and case_pattern(case) == "a.c"
)
assert compile_case_ids == (
    "workflow-compile-str-bounded-wildcard",
    "workflow-compile-str-bounded-wildcard-ignorecase",
)
assert pattern_case_ids == (
    "workflow-pattern-search-str-bounded-wildcard-ignorecase",
    "workflow-pattern-match-str-bounded-wildcard",
    "workflow-pattern-fullmatch-str-bounded-wildcard",
    "workflow-pattern-findall-str-bounded-wildcard",
    "workflow-pattern-finditer-str-bounded-wildcard",
    "workflow-pattern-search-str-bounded-wildcard-endpos-miss",
)
print("ok")
PY`

## Constraints
- Keep the change limited to `tests/python/test_module_workflow_parity_suite.py`. Do not widen into fixture manifest edits, benchmark workload edits, harness support modules, or feature-parity work in this run.
- Preserve the current bounded-wildcard compile and pattern subset order exactly; the point is to delete two owner-local mirrors, not to reinterpret which published rows define the bounded-wildcard slice.

## Notes
- `RBR-0909` is the next available architecture task id in the current checkout:
  - `rg -n 'RBR-0909' ops/state/backlog.md ops/state/current_status.md` returned no reserved follow-on id; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | rg '^RBR-0909'` returned no existing task file.
- There is no blocked architecture task to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 1`, `in_progress: 0`, `blocked: 0`, and `Last Cycle Anomalies: none`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The mirror target is concrete in the live checkout:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py` currently passes (`1301 passed, 1 skipped in 0.90s`);
  - `bash -lc "! rg -n '^MODULE_WORKFLOW_BOUNDED_WILDCARD_(COMPILE|PATTERN)_CASE_IDS = ' tests/python/test_module_workflow_parity_suite.py"` currently fails exactly on the remaining mirrors at lines `165` and `169`; and
  - the task-local probe in Acceptance already passes (`ok`), confirming the canonical `module-workflow-surface` bundle rows can recover the same ordered bounded-wildcard compile and pattern subsets without those handwritten case-id tuples.
- This stays on the same post-JSON parity-harness simplification track as the recent selector-mirror cleanup work:
  - `RBR-0897` removed the module-workflow pattern keyword fixture mirror;
  - `RBR-0903` removed duplicate correctness selector contracts from the grouped-capture owner path; and
  - `RBR-0907` removed the grouped-replacement collection selector mirror, leaving these bounded-wildcard case-id tuples as the next small owner-local mirrors to delete in the live module-workflow parity suite.

## Completion
- Removed `MODULE_WORKFLOW_BOUNDED_WILDCARD_COMPILE_CASE_IDS` and `MODULE_WORKFLOW_BOUNDED_WILDCARD_PATTERN_CASE_IDS` from `tests/python/test_module_workflow_parity_suite.py`.
- Added one live bounded-wildcard selector over loaded fixture rows and routed the compile/pattern subset helpers plus the bundle-contract check through that owner data path.
- Verified with:
  - `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py`
  - `bash -lc "! rg -n '^MODULE_WORKFLOW_BOUNDED_WILDCARD_(COMPILE|PATTERN)_CASE_IDS = ' tests/python/test_module_workflow_parity_suite.py"`
  - the task-local live-bundle probe from the acceptance block (`ok`)
