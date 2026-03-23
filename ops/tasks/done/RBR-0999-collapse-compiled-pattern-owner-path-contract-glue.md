## RBR-0999: Collapse compiled-pattern owner-path contract glue

Status: done
Owner: architecture-implementation
Created: 2026-03-23

## Goal
- Remove the remaining compiled-pattern owner-path publication scaffolding from `tests/python/test_module_workflow_parity_suite.py` so the two compiled-pattern publication tests run through one smaller file-local contract surface instead of open-coding fixture selection, signature-set setup, and row-alignment glue separately.

## Deliverables
- `tests/python/test_module_workflow_parity_suite.py`

## Acceptance Criteria
- `tests/python/test_module_workflow_parity_suite.py` adds one explicit file-local helper surface for the compiled-pattern module-helper publication contract, or a strictly smaller equivalent, that centralizes the remaining compiled-pattern-only setup currently split across:
  - `test_compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path()`
  - `test_module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases()`
- Repoint both tests through that shared contract surface instead of leaving all of the remaining compiled-pattern publication glue open-coded in test bodies:
  - a direct `published_fixture_cases = _published_owner_path_fixture_cases(... COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS ...)` selection in the keyword-frontier test;
  - a direct `published_fixture_signatures = {...}` setup for the same owner path; and
  - an inline `for row, fixture_case, direct_case in zip(...)` row-alignment loop in the compiled-pattern publication test.
- Preserve the current compiled-pattern owner-path publication contract exactly while shrinking the glue:
  - the compiled-pattern owner path still resolves to `62` published fixture rows and `62` selected direct rows;
  - the published text-model split stays `Counter({"str": 33, "bytes": 29})`;
  - the published helper split stays `Counter({"compile": 20, "search": 4, "match": 3, "fullmatch": 4, "split": 7, "findall": 2, "finditer": 2, "sub": 10, "subn": 10})`;
  - helper ordering still aligns through `_compiled_pattern_module_helper_publication_signature(case)[0]` rather than raw `.helper` access so compile rows keep mapping to `"compile"`;
  - row alignment still proves `fixture_case.case_id == row.fixture_case_id`, `direct_case is row.direct_case`, `fixture_case.use_compiled_pattern is True`, `fixture_case.text_model == row.text_model`, and `_compiled_pattern_module_helper_publication_signature(fixture_case) == _compiled_pattern_module_helper_publication_signature(direct_case)` for the full owner path.
- Preserve the scoped keyword-frontier assertions exactly while routing them through the shared compiled-pattern contract surface:
  - the six published fixture ids for the adjacent keyword-error and count-alias slice stay in the same order;
  - the explicit expected signatures for the two `published_after_positional_count_cases` remain unchanged;
  - the explicit expected signatures for the two `published_count_alias_cases` remain unchanged; and
  - the adjacent keyword-error, after-positional-count, and count-alias direct cases all remain members of the shared published compiled-pattern signature set.
- Keep the cleanup structural and file-local:
  - keep `_assert_owner_path_publication_contract(...)` and `_compiled_pattern_module_helper_publication_signature(...)` as the canonical lower-level primitives unless a strictly smaller file-local successor preserves the same verification surface;
  - do not widen this run into bounded-wildcard raw-module publication, non-compiled owner-path helpers, positional-indexlike helpers, manifests, harness modules, benchmark files, reports, or tracked state prose; and
  - do not add a shared helper module, registry, or checked-in data representation.

## Verification
- `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'`
- `PYTHONPATH=python:. ./.venv/bin/python - <<'PY'
from collections import Counter
from tests.python.test_module_workflow_parity_suite import (
    MODULE_CALL_CASES,
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
    _assert_owner_path_publication_contract,
    _compiled_pattern_module_helper_publication_signature,
)

published_fixture_cases, selected_direct_cases = _assert_owner_path_publication_contract(
    MODULE_CALL_CASES,
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
    expected_count=62,
    expected_text_model_counts=Counter({"str": 33, "bytes": 29}),
    expected_helper_counts=Counter(
        {
            "compile": 20,
            "search": 4,
            "match": 3,
            "fullmatch": 4,
            "split": 7,
            "findall": 2,
            "finditer": 2,
            "sub": 10,
            "subn": 10,
        }
    ),
    direct_case_helper=lambda case: _compiled_pattern_module_helper_publication_signature(case)[0],
)

for row, fixture_case, direct_case in zip(
    COMPILED_PATTERN_MODULE_HELPER_OWNER_PATH_ROWS,
    published_fixture_cases,
    selected_direct_cases,
):
    assert fixture_case.case_id == row.fixture_case_id
    assert direct_case is row.direct_case
    assert fixture_case.use_compiled_pattern is True
    assert fixture_case.text_model == row.text_model
    assert _compiled_pattern_module_helper_publication_signature(fixture_case) == (
        _compiled_pattern_module_helper_publication_signature(direct_case)
    )

print("ok")
PY`

## Constraints
- Keep the cleanup structural and local to `tests/python/test_module_workflow_parity_suite.py`.
- Prefer deleting repeated compiled-pattern contract glue over introducing another abstraction layer.
- Do not edit fixture manifests, benchmark workloads/tests, harness modules, reports, README/current-status/backlog prose, or non-parity test files in this run.

## Notes
- `RBR-0999` is unreserved in the live queue/state files for this run:
  - `rg -n 'RBR-0999|RBR-1000|RBR-1001|RBR-1002|RBR-1003' ops/state/backlog.md ops/state/current_status.md` returned no matches; and
  - `find ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked -maxdepth 1 -type f -printf '%f\n' | sort | tail -n 12` currently ends at `RBR-0998-publish-pattern-replacement-bytes-single-match-repeated-pair.md`.
- No blocked architecture task exists to reopen or normalize first because `ops/tasks/blocked/` is empty in the current checkout.
- The queue/runtime state does not trigger the shared-ready-queue stall no-op rule:
  - `.rebar/runtime/dashboard.md` reports `Dirty worktree: false`, `ready: 0`, `in_progress: 0`, `blocked: 0`, `tracked_json_blob_count: 0`, and `tracked_json_blob_delta: 0`; and
  - the latest recorded cycle shows both task workers finishing `done`, so there is no inherited-dirty checkpoint churn or stalled post-task refresh path to yield to.
- JSON burn-down remains complete in both tracked and live views, so this run stays on the post-JSON simplification lane:
  - `.rebar/runtime/dashboard.md` reports `tracked_json_blob_count: 0` and `tracked_json_blob_delta: 0`;
  - `git ls-files '*.json' | wc -l` returned `0`; and
  - `rg --files -g '*.json' | wc -l` returned `0`.
- The duplication target is concrete in the live checkout:
  - the focused pytest slice in Verification currently passes (`2 passed, 1449 deselected`);
  - the contract probe in Verification currently passes (`ok`); and
  - `python3 - <<'PY'
from pathlib import Path
text = Path("tests/python/test_module_workflow_parity_suite.py").read_text().splitlines()
for i, line in enumerate(text, start=1):
    if "published_fixture_cases = _published_owner_path_fixture_cases(" in line:
        print(i, line.strip())
    if "published_fixture_signatures = {" in line:
        print(i, line.strip())
    if "for row, fixture_case, direct_case in zip(" in line:
        print(i, line.strip())
PY` currently reports the remaining compiled-pattern glue at lines `4239`, `4243`, and `5071`, so this cleanup can stay structural and file-local.

## Completion Note
- Added one file-local `_assert_compiled_pattern_module_helper_publication_contract()` helper in `tests/python/test_module_workflow_parity_suite.py` that wraps the existing owner-path contract helper, preserves the exact 62-row compiled-pattern counts and signature ordering, and centralizes the row-alignment assertions and published signature set.
- Repointed both compiled-pattern publication tests through that shared helper so the keyword-frontier test no longer open-codes the owner-path fixture selection or signature-set build, and the compiled-pattern publication test no longer repeats the inline row-alignment loop.
- Verified with `PYTHONPATH=python:. ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_pattern_module_keyword_frontier_publishes_after_positional_count_cases_on_shared_owner_path or module_workflow_surface_publishes_compiled_pattern_module_helpers_from_direct_cases'` (`2 passed, 1449 deselected`) and with a repo-local Python probe that calls `_assert_compiled_pattern_module_helper_publication_contract()` (`ok`).
