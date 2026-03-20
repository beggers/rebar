# RBR-0751: Publish the module-workflow bounded wildcard compiled-pattern module-helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded-wildcard compiled-pattern module-helper pair, so the existing owner path starts publishing adjacent compiled-pattern `search()` / `match()` behavior for already-landed `a.c` support before the remaining compiled-pattern `fullmatch()` row or compiled-pattern collection-helper catch-up reopen the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern` and `workflow-module-match-str-bounded-wildcard-compiled-pattern`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`:
    - `compiled-module-search-ignorecase-bounded-hit`: `pattern == "a.c"`, `flags == 2`, `helper == "search"`, `use_compiled_pattern == True`, and `args == ["ABC"]`;
    - `compiled-module-match-bounded-hit`: `pattern == "a.c"`, default zero flags, `helper == "match"`, `use_compiled_pattern == True`, and `args == ["abc"]`;
  - keep both rows on the `str` text model; and
  - do not broaden into the remaining compiled-pattern bounded-wildcard `fullmatch()` row, compiled-pattern bounded-wildcard collection helpers, raw module-helper rows, bytes wildcard work, placeholder-path assertions, benchmark rows, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `46` total rows instead of `44`;
  - update the shared `module_call` helper breakdown so the owner path now expects `4` `search` rows, `3` `match` rows, `2` `fullmatch` rows, `1` `split` row, `1` `findall` row, and `2` `escape` rows;
  - keep the new rows pinned to the exact direct parity anchors `compiled-module-search-ignorecase-bounded-hit` and `compiled-module-match-bounded-hit` from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - extend the published compiled-pattern module-helper ownership so the bounded-wildcard pair sits alongside the already published literal and bytes-verbose compiled-pattern rows without forking a new helper registry or detached owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1414` total / `1414` passed / `0` `unimplemented` across `114` manifests to `1416` / `1416` / `0` across the same `114` manifests;
  - `module.workflow` moves from `44` / `44` / `0` to `46` / `46` / `0`;
  - `module.workflow.str` moves from `29` / `29` / `0` to `31` / `31` / `0`;
  - `module.workflow.module_call` moves from `11` / `11` / `0` to `13` / `13` / `0`; and
  - both new bounded-wildcard compiled-pattern module-helper rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0751-module-workflow-bounded-wildcard-compiled-module-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0751` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0750`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0749` on the same `module-workflow-surface` owner path so bounded-wildcard publication continues through compiled-pattern module helpers before the remaining compiled-pattern `fullmatch()` row or compiled-pattern collection-helper catch-up reopen the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-module-search-ignorecase-bounded-hit` and `compiled-module-match-bounded-hit` in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.search(rebar.compile("a.c", rebar.IGNORECASE), "ABC")` and `rebar.match(rebar.compile("a.c"), "abc")` already match CPython on match presence, group `0`, and spans `(0, 3)`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard_module_match_helpers_match_cpython or bounded_wildcard_module_collection_helpers_match_cpython'` passed in this run (`20 passed`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the bounded-wildcard raw module-level `search()` / `match()` / `fullmatch()` rows but no compiled-pattern bounded-wildcard module-helper rows, leaving this pair as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.
- `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a tracked state-prose change.

## Completion
- Added the two bounded-wildcard compiled-pattern `module_call` rows to `tests/conformance/fixtures/module_workflow_surface.py` without widening the manifest beyond the requested `search()` and `match()` pair.
- Kept the shared owner-path parity wiring on `tests/python/test_module_workflow_parity_suite.py`, extending the existing compiled-pattern module-helper ownership to reuse the direct bounded-wildcard anchors `compiled-module-search-ignorecase-bounded-hit` and `compiled-module-match-bounded-hit` from `BOUNDED_WILDCARD_MODULE_MATCH_CASES`.
- Regenerated `reports/correctness/latest.py`; the tracked published scorecard now reports `1416` total / `1416` passed / `0` unimplemented cases across `114` manifests, with `module.workflow` at `46/46/0`, `module.workflow.str` at `31/31/0`, and `module.workflow.module_call` at `13/13/0`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0751-module-workflow-bounded-wildcard-compiled-module-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
