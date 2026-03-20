# RBR-0745: Publish the module-workflow bounded wildcard pattern collection pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the next exact bounded-wildcard bound-`Pattern` collection-helper pair, so the existing owner path keeps publishing already-landed Rust-backed `a.c` behavior before returning to module-helper or compiled-pattern helper catch-up.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-findall-str-bounded-wildcard` and `workflow-pattern-finditer-str-bounded-wildcard`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES`:
    - `pattern-findall-bounded-default`: `pattern == "a.c"`, default zero flags, `helper == "findall"`, and `args == ["zabcaxcz", 1, 7]`;
    - `pattern-finditer-bounded-default`: `pattern == "a.c"`, default zero flags, `helper == "finditer"`, and `args == ["zabcaxcx", 1, 7]`;
  - keep both rows on the `str` text model; and
  - do not broaden into bounded-wildcard module-helper rows, compiled-pattern module-helper rows, bytes wildcard work, placeholder-path assertions, direct-test cleanup, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `41` total rows instead of `39`;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `9` `search` rows, `2` `match` rows, `8` `fullmatch` rows, `1` `findall` row, and `1` `finditer` row while leaving the compile, cache, purge, module-call, and escape buckets otherwise unchanged;
  - keep the new rows pinned to the exact direct parity anchors `pattern-findall-bounded-default` and `pattern-finditer-bounded-default` from `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES` instead of inventing another wildcard scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published bounded-wildcard ownership only to this exact bound-`Pattern` collection pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1409` total / `1409` passed / `0` `unimplemented` across `114` manifests to `1411` / `1411` / `0` across the same `114` manifests;
  - `module.workflow` moves from `39` / `39` / `0` to `41` / `41` / `0`;
  - `module.workflow.str` moves from `24` / `24` / `0` to `26` / `26` / `0`;
  - `module.workflow.pattern_call` moves from `19` / `19` / `0` to `21` / `21` / `0`; and
  - both new bounded-wildcard bound-`Pattern` collection rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0745-module-workflow-bounded-wildcard-pattern-collection-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0745` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0744`;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` do not reserve a newer tail id.
- Queue this directly behind the landed bounded-wildcard compile pair and bounded-wildcard bound-`Pattern` match-helper publication on the existing `module-workflow-surface` owner path, before bounded-wildcard module-helper rows or compiled-pattern module-helper catch-up.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-findall-bounded-default` and `pattern-finditer-bounded-default` in `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES`;
  - direct runtime probes in this run confirmed that `rebar.compile("a.c").findall("zabcaxcz", 1, 7)` and `list(rebar.compile("a.c").finditer("zabcaxcx", 1, 7))` already match CPython on result payloads and spans;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard and collection_helpers'` passed in this run; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added `workflow-pattern-findall-str-bounded-wildcard` and `workflow-pattern-finditer-str-bounded-wildcard` to `tests/conformance/fixtures/module_workflow_surface.py`, pinned to the existing `pattern-findall-bounded-default` and `pattern-finditer-bounded-default` anchors on the shared `BOUNDED_WILDCARD_PATTERN_COLLECTION_CASES` owner path.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared `module-workflow-surface` expectations now publish `41` rows total, with `pattern_call` helper counts of `search == 9`, `match == 2`, `fullmatch == 8`, `findall == 1`, and `finditer == 1`, while keeping the same compile, cache, purge, module-call, and escape buckets. The match-only compiled-pattern parity parametrizations were narrowed to match helpers so the new collection rows stay on the existing dedicated collection-helper coverage.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated `reports/correctness/latest.py`. Reading the tracked report artifact shows `1411` total / `1411` passed / `0` `unimplemented` across `114` manifests, with `module-workflow-surface` at `41` / `41` / `0`, `module.workflow` at `41` / `41` / `0`, `module.workflow.str` at `26` / `26` / `0`, and `module.workflow.pattern_call` at `21` / `21` / `0`; both new bounded-wildcard bound-`Pattern` collection rows are present in the tracked scorecard with `comparison == "pass"`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0745-module-workflow-bounded-wildcard-pattern-collection-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The task-local module-workflow report published `41` total / `41` passed / `0` `unimplemented`.
