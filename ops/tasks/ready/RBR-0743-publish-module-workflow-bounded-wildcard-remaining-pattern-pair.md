# RBR-0743: Publish the module-workflow bounded wildcard remaining pattern pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the remaining bounded-wildcard bound-`Pattern` helper pair, so the existing owner path keeps publishing already-landed Rust-backed `a.c` behavior instead of drifting back into shim-only compiled-pattern helper catch-up or jumping ahead to collection helpers.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-fullmatch-str-bounded-wildcard` and `workflow-pattern-search-str-bounded-wildcard-endpos-miss`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_PATTERN_MATCH_CASES`:
    - `pattern-fullmatch-bounded-hit`: `pattern == "a.c"`, default zero flags, `helper == "fullmatch"`, and `args == ["zaxcz", 1, 4]`;
    - `pattern-search-bounded-endpos-miss`: `pattern == "a.c"`, default zero flags, `helper == "search"`, and `args == ["zabc", 1, 3]`;
  - keep both rows on the `str` text model; and
  - do not broaden into bounded-wildcard collection helpers, direct module-helper rows, bytes wildcard work, placeholder-path assertions, compiled-pattern helper catch-up, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `39` total rows instead of `37`;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `9` `search` rows, `2` `match` rows, and `8` `fullmatch` rows while leaving the compile, cache, purge, module-call, and escape buckets otherwise unchanged;
  - keep the new rows pinned to the exact direct parity anchors `pattern-fullmatch-bounded-hit` and `pattern-search-bounded-endpos-miss` from `BOUNDED_WILDCARD_PATTERN_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published bounded-wildcard ownership only to this exact remaining bound-helper pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1407` total / `1407` passed / `0` `unimplemented` across `114` manifests to `1409` / `1409` / `0` across the same `114` manifests;
  - `module.workflow` moves from `37` / `37` / `0` to `39` / `39` / `0`;
  - `module.workflow.str` moves from `22` / `22` / `0` to `24` / `24` / `0`;
  - `module.workflow.pattern_call` moves from `17` / `17` / `0` to `19` / `19` / `0`; and
  - both new bounded-wildcard bound-helper rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0743-module-workflow-bounded-wildcard-remaining-pattern-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0743` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0742`;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - older missing ids exist in historical ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly behind the already published bounded-wildcard compile pair and first bounded-wildcard pattern-helper pair on the existing `module-workflow-surface` owner path, before bounded-wildcard collection helpers or any return to shim-only compiled-pattern helper publication.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-fullmatch-bounded-hit` and `pattern-search-bounded-endpos-miss` in `BOUNDED_WILDCARD_PATTERN_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.compile("a.c").fullmatch("zaxcz", 1, 4)` and `rebar.compile("a.c").search("zabc", 1, 3)` already match CPython on match presence, span, and group `0`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the bounded-wildcard compile pair plus the first bounded-wildcard bound-helper pair, but no remaining bounded-wildcard `fullmatch()` hit or bounded search-miss rows, leaving this pair as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.
