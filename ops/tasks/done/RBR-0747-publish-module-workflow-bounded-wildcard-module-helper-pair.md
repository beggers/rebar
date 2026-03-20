# RBR-0747: Publish the module-workflow bounded wildcard module-helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded-wildcard raw module-helper pair, so the existing owner path starts publishing adjacent `module_call` behavior for already-landed Rust-backed `a.c` support before returning to compiled-pattern wildcard helpers or broader collection-helper catch-up.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-search-str-bounded-wildcard-ignorecase` and `workflow-module-match-str-bounded-wildcard-miss`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`:
    - `module-search-ignorecase-bounded-hit`: `pattern == "a.c"`, `flags == 2`, `helper == "search"`, and `args == ["ABC"]`;
    - `module-match-bounded-miss`: `pattern == "a.c"`, default zero flags, `helper == "match"`, and `args == ["zabc"]`;
  - keep both rows on the `str` text model;
  - do not broaden into the raw bounded-wildcard `fullmatch()` module helper, raw collection helpers, compiled-pattern wildcard module helpers, bytes wildcard work, placeholder-path assertions, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `43` total rows instead of `41`;
  - update the shared `module_call` helper breakdown so the owner path now expects `3` `search` rows, `2` `match` rows, `1` `fullmatch` row, `1` `split` row, `1` `findall` row, and `2` `escape` rows;
  - keep the new rows pinned to the exact direct parity anchors `module-search-ignorecase-bounded-hit` and `module-match-bounded-miss` from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published bounded-wildcard ownership only to this exact raw module-helper pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1411` total / `1411` passed / `0` `unimplemented` across `114` manifests to `1413` / `1413` / `0` across the same `114` manifests;
  - `module.workflow` moves from `41` / `41` / `0` to `43` / `43` / `0`;
  - `module.workflow.str` moves from `26` / `26` / `0` to `28` / `28` / `0`;
  - `module.workflow.module_call` moves from `8` / `8` / `0` to `10` / `10` / `0`; and
  - both new bounded-wildcard raw module-helper rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0747-module-workflow-bounded-wildcard-module-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0747` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0746`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were otherwise empty in this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0745` on the same `module-workflow-surface` owner path so bounded-wildcard publication continues through raw module helpers before the remaining raw `fullmatch()` wildcard row, wildcard collection helpers, or any return to compiled-pattern wildcard helper catch-up.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-search-ignorecase-bounded-hit` and `module-match-bounded-miss` in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.search("a.c", "ABC", rebar.IGNORECASE)` and `rebar.match("a.c", "zabc")` already match CPython on match presence, group `0`, and spans where applicable;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard and module and not collection and not placeholder'` passed in this run;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes bounded-wildcard compile and bound-`Pattern` rows but no bounded-wildcard raw `module_call` rows, leaving this pair as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added `workflow-module-search-str-bounded-wildcard-ignorecase` and `workflow-module-match-str-bounded-wildcard-miss` to `tests/conformance/fixtures/module_workflow_surface.py`, pinned to the existing `module-search-ignorecase-bounded-hit` and `module-match-bounded-miss` anchors on the shared `BOUNDED_WILDCARD_MODULE_MATCH_CASES` owner path.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared `module-workflow-surface` expectations now publish `43` rows total, with `module_call` helper counts of `search == 3`, `match == 2`, `fullmatch == 1`, `split == 1`, `findall == 1`, and `escape == 2`. The parity suite now keeps the raw bounded-wildcard module-helper pair on its own direct-test bucket and asserts that the published fixture rows stay aligned with the exact shared direct anchors.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated `reports/correctness/latest.py`. Reading the tracked report artifact shows `1413` total / `1413` passed / `0` `unimplemented` across `114` manifests, with `module-workflow-surface` at `43` / `43` / `0`, `module.workflow` at `43` / `43` / `0`, `module.workflow.str` at `28` / `28` / `0`, and `module.workflow.module_call` at `10` / `10` / `0`; both new bounded-wildcard raw module-helper rows are present in the tracked scorecard with `comparison == "pass"`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0747-module-workflow-bounded-wildcard-module-helpers.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The task-local module-workflow report published `43` total / `43` passed / `0` `unimplemented`.
