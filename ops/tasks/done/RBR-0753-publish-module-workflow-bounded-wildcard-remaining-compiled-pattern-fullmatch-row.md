# RBR-0753: Publish the module-workflow bounded wildcard remaining compiled-pattern fullmatch row

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the remaining bounded-wildcard compiled-pattern module-helper `fullmatch()` row, so the existing owner path closes the bounded-wildcard compiled-pattern match-helper slice before compiled-pattern collection-helper catch-up reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`;
  - keep the row pinned to the exact adjacent direct parity anchor already defined on the shared owner path in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`:
    - `compiled-module-fullmatch-bounded-hit`: `pattern == "a.c"`, default zero flags, `helper == "fullmatch"`, `use_compiled_pattern == True`, and `args == ["abc"]`;
  - keep the row on the `str` text model; and
  - do not broaden into bounded-wildcard compiled-pattern collection helpers, raw module-helper rows, bytes wildcard work, placeholder-path assertions, benchmark rows, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `47` total rows instead of `46`;
  - update the shared `module_call` helper breakdown so the owner path now expects `4` `search` rows, `3` `match` rows, `3` `fullmatch` rows, `1` `split` row, `1` `findall` row, and `2` `escape` rows;
  - keep the new row pinned to the exact direct parity anchor `compiled-module-fullmatch-bounded-hit` from `BOUNDED_WILDCARD_MODULE_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - extend the published compiled-pattern module-helper ownership so the bounded-wildcard compiled-pattern match trio is complete without forking a new helper registry, direct-case mirror, or detached owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1416` total / `1416` passed / `0` `unimplemented` across `114` manifests to `1417` / `1417` / `0` across the same `114` manifests;
  - `module.workflow` moves from `46` / `46` / `0` to `47` / `47` / `0`;
  - `module.workflow.str` moves from `31` / `31` / `0` to `32` / `32` / `0`;
  - `module.workflow.module_call` moves from `13` / `13` / `0` to `14` / `14` / `0`; and
  - the new bounded-wildcard compiled-pattern `fullmatch()` row is visible in the tracked scorecard as a representative `module-workflow-surface` case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0753-module-workflow-bounded-wildcard-remaining-compiled-pattern-fullmatch-row.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0753` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0752`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0751` and `RBR-0752` on the same `module-workflow-surface` owner path so bounded-wildcard publication closes the remaining compiled-pattern `fullmatch()` row before compiled-pattern collection-helper catch-up reopens the frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchor `compiled-module-fullmatch-bounded-hit` in `BOUNDED_WILDCARD_MODULE_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.fullmatch(rebar.compile("a.c"), "abc")` already matches CPython on match presence, group `0`, and span `(0, 3)`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the bounded-wildcard raw module-level `search()` / `match()` / `fullmatch()` rows plus the compiled-pattern bounded-wildcard `search()` / `match()` pair, but not the remaining compiled-pattern bounded-wildcard `fullmatch()` row, leaving this exact row as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.
- `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a tracked state-prose change.

## Completion
- 2026-03-20: Added `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py`, extended the shared parity-owner expectations in `tests/python/test_module_workflow_parity_suite.py`, and refreshed the combined-scorecard representative case inventory in `tests/conformance/test_combined_correctness_scorecards.py`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0753-module-workflow-bounded-wildcard-remaining-compiled-pattern-fullmatch-row.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
- The tracked published scorecard changed in `reports/correctness/latest.py`: combined totals are now `1417` total / `1417` passed / `0` unimplemented across `114` manifests, `module.workflow` is `47` / `47` / `0`, `module.workflow.str` is `32` / `32` / `0`, and `module.workflow.module_call` is `14` / `14` / `0`.
