# RBR-0736: Publish the module-workflow literal str compiled-pattern module-helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded literal `str` module-level helper pair that accepts compiled patterns, so the existing owner path keeps publishing adjacent compiled-pattern `module_call` behavior without forking another manifest or jumping ahead to the wider collection/replacement helper set.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-search-str-compiled-pattern` and `workflow-module-match-str-compiled-pattern`;
  - keep both rows pinned to the exact adjacent direct parity cases already defined on the shared owner path:
    - `pattern == "abc"` for both rows;
    - use the default zero-flag path for both rows;
    - mark both rows with `use_compiled_pattern == True`;
    - `helper == "search"` with `args == ["zabczz"]` for `workflow-module-search-str-compiled-pattern`; and
    - `helper == "match"` with `args == ["abcdef"]` for `workflow-module-match-str-compiled-pattern`;
  - do not broaden into the literal `bytes` fullmatch sibling, compiled-pattern collection or replacement helpers, compiled-pattern type-error rows, keyword-argument helpers, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compiled-pattern-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `31` total rows instead of `29`;
  - update the shared `module_call` breakdown so the owner path now expects `2` `search` rows, `1` `match` row, `1` `fullmatch` row, and `2` `escape` rows;
  - keep the new rows pinned to the exact direct parity anchors `compiled-pattern-search-str` and `compiled-pattern-match-str` from `COMPILED_PATTERN_MODULE_HELPER_CASES` instead of inventing another literal-only scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published compiled-module-helper ownership to include the new literal `str` pair alongside the already published bytes verbose pair.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1399` total / `1399` passed / `0` `unimplemented` across `114` manifests to `1401` / `1401` / `0` across the same `114` manifests;
  - `module.workflow` moves from `29` / `29` / `0` to `31` / `31` / `0`;
  - `module.workflow.str` moves from `15` / `15` / `0` to `17` / `17` / `0`; and
  - `module.workflow.module_call` moves from `4` / `4` / `0` to `6` / `6` / `0`, with both new compiled-pattern literal `str` rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0736-module-workflow-literal-str-compiled-pattern-module-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern module-helper publication file.

## Notes
- `RBR-0736` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0735`;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - older missing ids exist in historical ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after `RBR-0734` so the same compiled-pattern module-helper family continues on the existing `module-workflow-surface` owner path instead of jumping to collection helpers or another manifest.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-search-str` and `compiled-pattern-match-str` in `COMPILED_PATTERN_MODULE_HELPER_CASES`;
  - a direct runtime probe in this run confirmed that `rebar.search(rebar.compile("abc"), "zabczz")` and `rebar.match(rebar.compile("abc"), "abcdef")` already match CPython with spans `(1, 4)` and `(0, 3)`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes only the bytes verbose compiled-pattern `module_call` pair plus `escape()` rows, leaving this literal `str` pair as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.
