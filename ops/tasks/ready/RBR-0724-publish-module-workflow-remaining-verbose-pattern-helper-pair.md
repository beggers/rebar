# RBR-0724: Publish the remaining module-workflow verbose pattern-helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the remaining positive compiled-pattern `search()` / `fullmatch()` pair from the shared verbose regression table, so the already-exercised str verbose helper path is published on the existing owner surface before bytes siblings, miss-path rows, or another module-workflow branch broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-str-verbose-regression-digits` and `workflow-pattern-fullmatch-str-verbose-regression-alpha` beside the existing verbose regression helper rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "str"` for both new rows;
    - `helper == "search"` with `args == ["prefix\nENV_VAR = 123\nsuffix"]` for `workflow-pattern-search-str-verbose-regression-digits`; and
    - `helper == "fullmatch"` with `args == ["ENV_VAR   =   ABCD"]` for `workflow-pattern-fullmatch-str-verbose-regression-alpha`;
  - do not broaden into bytes siblings, miss-path rows, multiline-only helpers, module-helper rows, cache-state variants, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another regression-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `19` total rows instead of `17`;
  - update the pattern-call breakdown so the shared owner path now expects `3` `search` rows, `1` `match` row, and `3` `fullmatch` rows on the published manifest;
  - keep the existing `VERBOSE_COMPILE_WORKFLOW_CASES` as the source of truth for this exact helper pair, and pin the published manifest to the remaining positive direct cases `search-multiline-middle-line-digits` and `fullmatch-alpha-with-extra-whitespace` instead of creating another file-local scenario table; and
  - do not add a new parity module, a detached regression helper fixture, bytes helper expectations, or verbose miss-row publication in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1387` total / `1387` passed / `0` `unimplemented` across `114` manifests to `1389` / `1389` / `0` across the same `114` manifests;
  - `module.workflow` moves from `17` total / `17` passed / `0` `unimplemented` to `19` / `19` / `0`;
  - `module.workflow.str` moves from `11` total / `11` passed / `0` `unimplemented` to `13` / `13` / `0`; and
  - `module.workflow.pattern_call` moves from `5` total / `5` passed / `0` `unimplemented` to `7` / `7` / `0`, with both new regression helper rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0724-module-workflow-remaining-verbose-patterns.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, or benchmark reports in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached regression workflow helper just for this pair.
- Keep any later bytes-helper follow-on or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0724` is the next available feature task id in the current checkout; `RBR-0723` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0724" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly after the drained `RBR-0722` head so the shared verbose compiled-pattern helper frontier keeps moving on the existing module-workflow owner path instead of pausing for a new branch.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0722-publish-module-workflow-verbose-pattern-helper-pair.md` closed the first published verbose helper pair and left the feature queue empty;
  - `tests/python/test_module_workflow_parity_suite.py` already defines six `VERBOSE_COMPILE_WORKFLOW_CASES`, of which four are positive direct parity scenarios; after `RBR-0722`, the remaining unpublished positive pair is `search-multiline-middle-line-digits` plus `fullmatch-alpha-with-extra-whitespace`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes only `workflow-pattern-search-str-verbose-regression` and `workflow-pattern-fullmatch-str-verbose-regression` for the verbose compiled-pattern owner path, but not the remaining positive search/fullmatch companions from the same direct table;
  - `tests/conformance/test_combined_correctness_scorecards.py` currently names the existing two verbose helper rows as representative `module-workflow-surface` pattern-call coverage, but not the remaining positive pair already exercised in the direct parity suite; and
  - `reports/correctness/latest.py` currently reports `1387` total / `1387` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `17` / `17` / `0`, `module.workflow.str` at `11` / `11` / `0`, and `module.workflow.pattern_call` at `5` / `5` / `0`, so this slice extends the tracked frontier through adjacent published-owner coverage rather than a new family.
