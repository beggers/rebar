# RBR-0428: Publish the module-workflow bounded wildcard pattern-helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded wildcard bound-`Pattern` helper pair, so the existing owner path keeps publishing already-landed Rust-backed `a.c` execution behavior instead of drifting back into shim-only compiled-pattern helper catch-up or jumping ahead to collection helpers.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-str-bounded-wildcard-ignorecase` and `workflow-pattern-match-str-bounded-wildcard`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `BOUNDED_WILDCARD_PATTERN_MATCH_CASES`:
    - `pattern-search-ignorecase-bounded-hit`: `pattern == "a.c"`, `flags == int(re.IGNORECASE)`, `helper == "search"`, and `args == ["zaBczz", 1, 5]`;
    - `pattern-match-bounded-hit`: `pattern == "a.c"`, default zero flags, `helper == "match"`, and `args == ["zabcaxc", 1, 4]`;
  - keep both rows on the `str` text model; and
  - do not broaden into the remaining bounded-wildcard `fullmatch()` hit, the bounded-wildcard search miss, collection helpers, direct module-helper rows, bytes wildcard work, placeholder-path assertions, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another wildcard-specific manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `37` total rows instead of `35`;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `8` `search` rows, `2` `match` rows, and `7` `fullmatch` rows while leaving the compile, cache, purge, module-call, and escape buckets otherwise unchanged;
  - keep the new rows pinned to the exact direct parity anchors `pattern-search-ignorecase-bounded-hit` and `pattern-match-bounded-hit` from `BOUNDED_WILDCARD_PATTERN_MATCH_CASES` instead of inventing another wildcard scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published bounded-wildcard ownership only to this exact bound-helper pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1405` total / `1405` passed / `0` `unimplemented` across `114` manifests to `1407` / `1407` / `0` across the same `114` manifests;
  - `module.workflow` moves from `35` / `35` / `0` to `37` / `37` / `0`;
  - `module.workflow.str` moves from `20` / `20` / `0` to `22` / `22` / `0`; and
  - both new bounded-wildcard bound-helper rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0428-module-workflow-bounded-wildcard-pattern-helper-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bounded-wildcard publication file.

## Notes
- `RBR-0428` is the next available task id in the current checkout:
  - a repo scan across `ops/tasks/{ready,in_progress,done,blocked}` plus reserved ids named in `ops/state/backlog.md` and `ops/state/current_status.md` left `RBR-0428` as the first unclaimed identifier, even though later historical ids already exist from previous queue shaping;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - no blocked feature task exists to reopen first on the current bounded-wildcard frontier.
- Queue this directly after `RBR-0740` so the same bounded-wildcard family continues on the existing `module-workflow-surface` owner path before the unpublished bounded-wildcard `fullmatch()` / miss rows, collection helpers, or any return to shim-only compiled-pattern helper publication.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-search-ignorecase-bounded-hit` and `pattern-match-bounded-hit` in `BOUNDED_WILDCARD_PATTERN_MATCH_CASES`;
  - direct runtime probes in this run confirmed that `rebar.compile("a.c", rebar.IGNORECASE).search("zaBczz", 1, 5)` and `rebar.compile("a.c").match("zabcaxc", 1, 4)` already match CPython on group `0` and span, while the surrounding bounded-wildcard probe also confirmed the adjacent compile, `search`, `fullmatch`, `findall`, and `finditer` behaviors are already landed on the same owner path;
  - a targeted parity run in this run passed for the bounded-wildcard direct tests and helper parametrizations: `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'bounded_wildcard and (compile_metadata or pattern_match_helpers or pattern_collection_helpers or direct_workflow)'`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes only the bounded-wildcard compile pair for `a.c`, plus no bounded-wildcard `pattern_call` rows at all, leaving this bound-helper pair as the next bounded adjacent publication on the same owner path; and
  - `ops/state/backlog.md` and `ops/state/current_status.md` already honestly say that no ready feature follow-on survives behind the active bounded-wildcard publication slice, so no tracked state prose needed refresh for this one-task refill.
