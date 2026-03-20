# RBR-0726: Publish the module-workflow verbose miss-path helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the two remaining negative compiled-pattern `search()` / `fullmatch()` rows from the shared verbose regression table, so the existing str verbose helper family is fully published on the current owner path before bytes helpers, benchmark expansion, or another module-workflow branch broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add one `search()` miss row and one `fullmatch()` miss row beside the existing verbose regression helper rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "str"` for both new rows;
    - `helper == "search"` with `args == ["prefix\nENV_VAR = 12345\nsuffix"]` for the too-many-digits miss row; and
    - `helper == "fullmatch"` with `args == ["env_var = 123"]` for the lowercase-key miss row;
  - keep these rows pinned to the remaining direct cases `search-rejects-too-many-digits` and `fullmatch-rejects-lowercase-key` from `VERBOSE_COMPILE_WORKFLOW_CASES`; and
  - do not broaden into bytes siblings, positive helper rows already published by `RBR-0722` and `RBR-0724`, module-helper rows, cache-state variants, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another verbose-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `21` total rows instead of `19`;
  - update the `pattern_call` breakdown so the shared owner path now expects `4` `search` rows, `1` `match` row, and `4` `fullmatch` rows on the published manifest;
  - keep `VERBOSE_COMPILE_WORKFLOW_CASES` as the source of truth for this exact helper pair, and pin the published miss rows directly to `search-rejects-too-many-digits` and `fullmatch-rejects-lowercase-key` instead of creating another scenario table; and
  - do not add a new parity module, a detached verbose miss fixture, bytes helper expectations, or benchmark assertions in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1389` total / `1389` passed / `0` `unimplemented` across `114` manifests to `1391` / `1391` / `0` across the same `114` manifests;
  - `module.workflow` moves from `19` total / `19` passed / `0` `unimplemented` to `21` / `21` / `0`;
  - `module.workflow.str` moves from `13` total / `13` passed / `0` `unimplemented` to `15` / `15` / `0`; and
  - `module.workflow.pattern_call` moves from `7` total / `7` passed / `0` `unimplemented` to `9` / `9` / `0`, with both new verbose miss rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0726-module-workflow-verbose-miss-paths.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, or native-boundary scaffolding in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached helper table for this pair.
- Keep any later bytes-helper follow-on or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0726` is the next available feature task id in the current checkout; the current task tail runs through `RBR-0725`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty, and there are no reserved missing tail ids in `ops/state/backlog.md` or `ops/state/current_status.md`.
- Queue this directly after the drained `RBR-0724` head so the shared verbose compiled-pattern helper frontier finishes the already-anchored str table before bytes-helper publication or another module-workflow branch reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0724-publish-module-workflow-remaining-verbose-pattern-helper-pair.md` closed the last unpublished positive helper pair and left the feature queue empty;
  - `tests/python/test_module_workflow_parity_suite.py` already defines six `VERBOSE_COMPILE_WORKFLOW_CASES`, and after `RBR-0724` the only unpublished rows from that direct table are `search-rejects-too-many-digits` and `fullmatch-rejects-lowercase-key`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes four positive verbose regression `pattern_call` rows on `module-workflow-surface`, but no verbose miss-path companions from the same direct parity table;
  - `tests/conformance/test_combined_correctness_scorecards.py` currently names the four positive verbose helper rows as representative `module-workflow-surface` pattern-call coverage, but not the remaining negative pair already exercised in the direct parity suite; and
  - `reports/correctness/latest.py` currently reports `1389` total / `1389` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `19` / `19` / `0`, `module.workflow.str` at `13` / `13` / `0`, and `module.workflow.pattern_call` at `7` / `7` / `0`, so this slice extends the tracked frontier through adjacent owner-path publication rather than a new family.
