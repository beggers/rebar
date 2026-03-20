# RBR-0733: Publish the module-workflow bytes verbose miss-path helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the remaining negative `bytes` compiled-pattern `search()` / `fullmatch()` verbose regression helper pair, so the bytes verbose helper table is fully published on the existing `module-workflow-surface` owner path before module-helper publication, benchmark catch-up, or another module-workflow branch broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-bytes-verbose-regression-too-many-digits` and `workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key` beside the existing bytes verbose helper rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "bytes"` for both new rows;
    - `helper == "search"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "prefix\\nENV_VAR = 12345\\nsuffix"}]` for `workflow-pattern-search-bytes-verbose-regression-too-many-digits`; and
    - `helper == "fullmatch"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "env_var = 123"}]` for `workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key`;
  - keep these rows pinned to the remaining direct miss cases `search-rejects-too-many-digits` and `fullmatch-rejects-lowercase-key` from `VERBOSE_COMPILE_WORKFLOW_CASES`; and
  - do not broaden into module-helper rows, multiline-only helper variants, cache-state variants, benchmark rows, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another verbose-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `27` total rows instead of `25`;
  - update the `pattern_call` breakdown so the shared owner path now expects `7` `search` rows, `1` `match` row, and `7` `fullmatch` rows on the published manifest;
  - keep the bytes miss pair tied to the existing verbose owner data:
    - reuse `VERBOSE_COMPILE_WORKFLOW_CASES` as the source of truth for the `str` payloads and assert that the new bytes rows carry the same payloads encoded to bytes;
    - keep `VERBOSE_BYTES_COMPILE_CASE_ID`, `VERBOSE_BYTES_SEARCH_PATTERN_CASE`, and `VERBOSE_BYTES_FULLMATCH_PATTERN_CASE` as the shared bytes compile/helper anchors instead of creating another bytes-specific scenario table or parity module; and
    - do not add detached bytes helper fixtures, module-helper publication, or benchmark assertions in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1395` total / `1395` passed / `0` `unimplemented` across `114` manifests to `1397` / `1397` / `0` across the same `114` manifests;
  - `module.workflow` moves from `25` / `25` / `0` to `27` / `27` / `0`;
  - `module.workflow.bytes` moves from `10` / `10` / `0` to `12` / `12` / `0`; and
  - `module.workflow.pattern_call` moves from `13` / `13` / `0` to `15` / `15` / `0`, with both new bytes verbose miss rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0733-module-workflow-bytes-verbose-miss-paths.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, README text, or harness files in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bytes-only helper table for this pair.
- Keep any later module-helper publication or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0733` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0732`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty at the start of this run, and no newer tail id is reserved in `ops/state/backlog.md` or `ops/state/current_status.md`; and
  - older missing ids exist in historical task ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after the drained `RBR-0731` head so the shared bytes verbose compiled-pattern helper frontier finishes the already-anchored table on the same module-workflow owner path instead of pausing for module-helper publication or a different family.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0731-publish-module-workflow-remaining-positive-bytes-verbose-helper-pair.md` closed the last unpublished positive bytes helper pair and left the feature queue empty;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes four positive bytes verbose `pattern_call` rows on `module-workflow-surface`, but no bytes miss-path companions from the same direct parity table;
  - `tests/python/test_module_workflow_parity_suite.py` already defines the shared six-case `VERBOSE_COMPILE_WORKFLOW_CASES`, pins the published bytes rows to the positive direct cases, and therefore leaves `search-rejects-too-many-digits` plus `fullmatch-rejects-lowercase-key` as the next bounded bytes pair on the same owner path;
  - a direct runtime probe in this run confirmed that `rebar.compile(b"^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $", re.MULTILINE | re.VERBOSE)` already matches CPython for all six bytes verbose helper cases, including both miss-path rows returning `None`; and
  - `reports/correctness/latest.py` currently reports `1395` total / `1395` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `25` / `25` / `0`, `module.workflow.bytes` at `10` / `10` / `0`, and `module.workflow.pattern_call` at `13` / `13` / `0`, so this slice extends the tracked frontier through adjacent owner-path publication rather than a new family.

## Completion
- 2026-03-20: Added `workflow-pattern-search-bytes-verbose-regression-too-many-digits` and `workflow-pattern-fullmatch-bytes-verbose-regression-lowercase-key` to `tests/conformance/fixtures/module_workflow_surface.py`, keeping the existing verbose regression pattern, `flags == 72`, `text_model == "bytes"`, and only the two miss-path compiled-pattern helper rows requested by this task.
- Updated `tests/python/test_module_workflow_parity_suite.py` on the shared owner path so the published `module-workflow-surface` bundle now expects `27` rows instead of `25`, the `pattern_call` helper mix is `7` `search` / `1` `match` / `7` `fullmatch`, and the new bytes miss rows are pinned back to `VERBOSE_COMPILE_WORKFLOW_CASES` with their payloads encoded through the existing bytes compile anchor.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated the tracked `reports/correctness/latest.py` publication. The tracked artifact now reads `1397` total / `1397` passed / `0` `unimplemented` across `114` manifests overall, with `module.workflow` at `27` / `27` / `0`, `module.workflow.bytes` at `12` / `12` / `0`, and `module.workflow.pattern_call` at `15` / `15` / `0`; both new bytes verbose miss rows are present in the tracked report.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0733-module-workflow-bytes-verbose-miss-paths.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The task-local module-workflow report published `27` total / `27` passed / `0` `unimplemented`.
