# RBR-0755: Publish the module-workflow remaining compiled-pattern `finditer()` row

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the remaining compiled-pattern module-level collection-helper row, so the existing owner path catches the adjacent compiled-pattern `finditer()` workflow up on the published correctness surface before replacement-oriented compiled-pattern helpers or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-finditer-str-compiled-pattern`;
  - keep the row pinned to the exact adjacent direct parity anchor already defined on the shared owner path in `COMPILED_PATTERN_MODULE_HELPER_CASES`:
    - `compiled-pattern-finditer-str`: `pattern == "abc"`, default zero flags, `helper == "finditer"`, `args == ["zabcabc"]`, and `result_kind == "iter"`;
  - keep the row on the `str` text model with `use_compiled_pattern == True`; and
  - do not broaden into compiled-pattern replacement helpers, bounded-wildcard raw collection helpers, bytes collection variants, benchmark rows, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compiled-pattern collection manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `48` total rows instead of `47`;
  - update the shared `module_call` helper breakdown so the owner path now expects `4` `search` rows, `3` `match` rows, `3` `fullmatch` rows, `1` `split` row, `1` `findall` row, `1` `finditer` row, and `2` `escape` rows;
  - extend the published compiled-pattern module-helper ownership by exactly one row so the canonical published slice now includes `workflow-module-finditer-str-compiled-pattern` beside the existing literal `split`, bytes `findall`, literal `search`/`match`, bounded-wildcard compiled `search`/`match`/`fullmatch`, and bytes verbose compiled `search`/`fullmatch` rows;
  - keep the new row pinned to the exact direct anchor `compiled-pattern-finditer-str` instead of inventing another collection-helper table or detached owner path; and
  - keep the published compiled-pattern direct-case alignment honest by updating the canonical selected direct-case sequence and text-model subset assertions without restoring any mirrored subset sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1417` total / `1417` passed / `0` `unimplemented` across `114` manifests to `1418` / `1418` / `0` across the same `114` manifests;
  - `module.workflow` moves from `47` / `47` / `0` to `48` / `48` / `0`;
  - `module.workflow.str` moves from `32` / `32` / `0` to `33` / `33` / `0`;
  - `module.workflow.module_call` moves from `14` / `14` / `0` to `15` / `15` / `0`; and
  - the new compiled-pattern `finditer()` row is visible in the tracked scorecard as a representative `module-workflow-surface` case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0755-module-workflow-remaining-compiled-pattern-finditer-row.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern collection publication file.

## Notes
- `RBR-0755` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0754`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` were otherwise empty in this run; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly after `RBR-0753` on the same `module-workflow-surface` owner path. `RBR-0754` is architecture cleanup, so it does not change the feature frontier.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchor `compiled-pattern-finditer-str` in `COMPILED_PATTERN_MODULE_HELPER_CASES`;
  - direct runtime probing in this run confirmed that `list(rebar.finditer(rebar.compile("abc"), "zabcabc"))` matches CPython on group `0`, spans, and `regs`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'compiled_patterns and finditer or literal_collection_matrix_module_helpers_accept_compiled_patterns'` passed in this run (`10 passed, 645 deselected`); and
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the compiled-pattern module-level `split()` and `findall()` collection helpers but not the adjacent compiled-pattern `finditer()` row, leaving this as the next bounded catch-up slice on the same owner path.
- `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a tracked state-prose change.

## Completion
- 2026-03-20: Added `workflow-module-finditer-str-compiled-pattern` to `tests/conformance/fixtures/module_workflow_surface.py`, extended the shared owner-path expectations in `tests/python/test_module_workflow_parity_suite.py`, and refreshed the combined scorecard representative-case list in `tests/conformance/test_combined_correctness_scorecards.py`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0755-module-workflow-remaining-compiled-pattern-finditer-row.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and a post-publication `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/conformance/test_combined_correctness_scorecards.py`.
- The tracked published scorecard changed in `reports/correctness/latest.py`: combined totals are now `1418` total / `1418` passed / `0` unimplemented across `114` manifests, `module.workflow` is `48` / `48` / `0`, `module.workflow.str` is `33` / `33` / `0`, and `module.workflow.module_call` is `15` / `15` / `0`.
