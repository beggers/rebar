# RBR-0749: Publish the module-workflow bounded wildcard remaining raw fullmatch row

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the remaining bounded-wildcard raw module-level `fullmatch()` workflow, so the existing owner path finishes the direct raw module-helper bounded-wildcard slice before wildcard collection helpers or broader compiled-pattern helper catch-up reopen the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-fullmatch-str-bounded-wildcard`;
  - keep that row pinned to the exact direct parity anchor already defined on the shared owner path in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`:
    - `module-fullmatch-bounded-hit`: `pattern == "a.c"`, default zero flags, `helper == "fullmatch"`, and `args == ["abc"]`;
  - keep the row on the `str` text model; and
  - do not broaden into raw module-level collection helpers, compiled-pattern bounded-wildcard module helpers, bytes wildcard work, placeholder-path assertions, benchmark rows, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `44` total rows instead of `43`;
  - update the shared `module_call` helper breakdown so the owner path now expects `3` `search` rows, `2` `match` rows, `2` `fullmatch` rows, `1` `split` row, `1` `findall` row, and `2` `escape` rows;
  - keep the new row pinned to the exact direct parity anchor `module-fullmatch-bounded-hit` from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - extend the published bounded-wildcard raw module-helper alignment so the selected published fixture rows stay matched to the exact direct anchors `module-search-ignorecase-bounded-hit`, `module-match-bounded-miss`, and `module-fullmatch-bounded-hit` on the shared owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1413` total / `1413` passed / `0` `unimplemented` across `114` manifests to `1414` / `1414` / `0` across the same `114` manifests;
  - `module.workflow` moves from `43` / `43` / `0` to `44` / `44` / `0`;
  - `module.workflow.str` moves from `28` / `28` / `0` to `29` / `29` / `0`;
  - `module.workflow.module_call` moves from `10` / `10` / `0` to `11` / `11` / `0`; and
  - the new bounded-wildcard raw `fullmatch()` row is visible in the tracked scorecard as a representative `module-workflow-surface` case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0749-module-workflow-bounded-wildcard-remaining-raw-fullmatch.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python - <<'PY'
import tests.python.test_module_workflow_parity_suite as mod

selected_direct_cases = tuple(
    case
    for case in mod.BOUNDED_WILDCARD_MODULE_MATCH_CASES
    if case.case_id in (
        "module-search-ignorecase-bounded-hit",
        "module-match-bounded-miss",
        "module-fullmatch-bounded-hit",
    )
)

assert tuple(case.case_id for case in selected_direct_cases) == (
    "module-search-ignorecase-bounded-hit",
    "module-match-bounded-miss",
    "module-fullmatch-bounded-hit",
)
assert tuple(case.case_id for case in mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES) == (
    "workflow-module-search-str-bounded-wildcard-ignorecase",
    "workflow-module-match-str-bounded-wildcard-miss",
    "workflow-module-fullmatch-str-bounded-wildcard",
)
assert tuple(case.helper for case in mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES) == tuple(
    case.helper for case in selected_direct_cases
)
for fixture_case, direct_case in zip(
    mod.PUBLISHED_BOUNDED_WILDCARD_RAW_MODULE_HELPER_CASES,
    selected_direct_cases,
):
    assert fixture_case.use_compiled_pattern is False
    assert fixture_case.text_model == "str"
    assert mod.case_pattern(fixture_case) == direct_case.pattern
    assert tuple(fixture_case.args) == (direct_case.string,)
    assert fixture_case.flags == direct_case.flags
print("ok")
PY`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0749` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0748`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0747` on the same `module-workflow-surface` owner path. `RBR-0748` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact remaining direct parity anchor `module-fullmatch-bounded-hit` in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.fullmatch("a.c", "abc")` matches CPython on match presence, group `0`, and span;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard and module and not placeholder'` passed in this run;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the bounded-wildcard raw module-level `search()` and `match()` rows but no raw `fullmatch()` row, leaving this as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added `workflow-module-fullmatch-str-bounded-wildcard` to `tests/conformance/fixtures/module_workflow_surface.py`, pinned to the existing `module-fullmatch-bounded-hit` anchor on the shared `BOUNDED_WILDCARD_MODULE_MATCH_CASES` owner path.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared `module-workflow-surface` expectations now publish `44` rows total, with `module_call` helper counts of `search == 3`, `match == 2`, `fullmatch == 2`, `split == 1`, `findall == 1`, and `escape == 2`. The parity suite now keeps the bounded-wildcard raw module-helper alignment on the exact `module-search-ignorecase-bounded-hit`, `module-match-bounded-miss`, and `module-fullmatch-bounded-hit` direct anchors.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated `reports/correctness/latest.py`. Reading the tracked report artifact after regeneration shows `1414` total / `1414` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `44` / `44` / `0`, `module.workflow.str` at `29` / `29` / `0`, and `module.workflow.module_call` at `11` / `11` / `0`; the new bounded-wildcard raw `fullmatch()` row is present in the tracked scorecard as `workflow-module-fullmatch-str-bounded-wildcard`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0749-module-workflow-bounded-wildcard-remaining-raw-fullmatch.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and the direct alignment probe from the acceptance criteria. The task-local module-workflow report published `44` total / `44` passed / `0` `unimplemented`.
