# RBR-0731: Publish the remaining positive module-workflow bytes verbose helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the remaining positive `bytes` compiled-pattern `search()` / `fullmatch()` verbose regression helper pair, so the already-published bytes verbose helper anchors grow on the existing owner path before bytes miss-path rows, module-helper publication, benchmark catch-up, or another module-workflow branch broadens this family.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-bytes-verbose-regression-digits` and `workflow-pattern-fullmatch-bytes-verbose-regression-alpha` beside the existing bytes verbose helper rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "bytes"` for both new rows;
    - `helper == "search"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "prefix\\nENV_VAR = 123\\nsuffix"}]` for `workflow-pattern-search-bytes-verbose-regression-digits`; and
    - `helper == "fullmatch"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "ENV_VAR   =   ABCD"}]` for `workflow-pattern-fullmatch-bytes-verbose-regression-alpha`;
  - keep these rows pinned to the remaining positive direct cases `search-multiline-middle-line-digits` and `fullmatch-alpha-with-extra-whitespace` from `VERBOSE_COMPILE_WORKFLOW_CASES`; and
  - do not broaden into bytes miss-path rows, module-helper rows, multiline-only helper variants, cache-state variants, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another verbose-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `25` total rows instead of `23`;
  - update the `pattern_call` breakdown so the shared owner path now expects `6` `search` rows, `1` `match` row, and `6` `fullmatch` rows on the published manifest;
  - keep the bytes helper pair tied to the existing verbose owner data:
    - reuse `VERBOSE_COMPILE_WORKFLOW_CASES` as the source of truth for the `str` payloads and assert that the new bytes rows carry the same payloads encoded to bytes;
    - keep `VERBOSE_BYTES_COMPILE_CASE_ID`, `VERBOSE_BYTES_SEARCH_PATTERN_CASE`, and `VERBOSE_BYTES_FULLMATCH_PATTERN_CASE` as the shared bytes compile/helper anchors instead of creating another bytes-specific scenario table or parity module; and
    - do not add detached bytes helper fixtures, module-helper publication, or benchmark assertions in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1393` total / `1393` passed / `0` `unimplemented` across `114` manifests to `1395` / `1395` / `0` across the same `114` manifests;
  - `module.workflow` moves from `23` / `23` / `0` to `25` / `25` / `0`;
  - `module.workflow.bytes` moves from `8` / `8` / `0` to `10` / `10` / `0`; and
  - `module.workflow.pattern_call` moves from `11` / `11` / `0` to `13` / `13` / `0`, with both new bytes verbose helper rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0731-module-workflow-remaining-positive-bytes-verbose-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, README text, or harness files in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached bytes-only helper table for this pair.
- Keep any later bytes miss-path follow-on, module-helper publication, or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0731` is the next available feature task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0730`, `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` are empty at the start of this run, and no newer tail id is reserved in `ops/state/backlog.md` or `ops/state/current_status.md`; and
  - older missing ids exist in historical task ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after the drained `RBR-0726` head so the shared verbose compiled-pattern helper frontier keeps moving on the same module-workflow owner path instead of pausing for a different family.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the tracked frontier:
  - `ops/tasks/done/RBR-0726-publish-module-workflow-verbose-miss-path-helper-pair.md` closed the remaining `str` miss-path publication pair and left the feature queue empty;
  - `ops/tasks/done/RBR-0417-land-module-workflow-bytes-verbose-pattern-execution.md` already landed Rust-backed bytes verbose compiled-pattern execution for all six positive and miss direct cases on this anchored owner path, so the next slice can stay publication-only;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes only `workflow-pattern-search-bytes-verbose-regression` and `workflow-pattern-fullmatch-bytes-verbose-regression` for the bytes verbose helper surface, leaving the direct positive digits/alpha companions unpublished on the same manifest;
  - `tests/python/test_module_workflow_parity_suite.py` already defines the shared six-case `VERBOSE_COMPILE_WORKFLOW_CASES`, pins the published bytes rows to `search-multiline-middle-line-alpha` and `fullmatch-digits-without-literal-spaces`, and therefore leaves `search-multiline-middle-line-digits` plus `fullmatch-alpha-with-extra-whitespace` as the next bounded positive bytes pair on the same owner path; and
  - `reports/correctness/latest.py` currently reports `1393` total / `1393` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `23` / `23` / `0`, `module.workflow.bytes` at `8` / `8` / `0`, and `module.workflow.pattern_call` at `11` / `11` / `0`, so this slice extends the tracked frontier through adjacent owner-path publication rather than a new family.

## Completion
- 2026-03-20: Added `workflow-pattern-search-bytes-verbose-regression-digits` and `workflow-pattern-fullmatch-bytes-verbose-regression-alpha` to `tests/conformance/fixtures/module_workflow_surface.py`, keeping the existing verbose regression pattern, `flags == 72`, `text_model == "bytes"`, and only the two positive compiled-pattern helper rows requested by this task.
- Updated `tests/python/test_module_workflow_parity_suite.py` on the shared owner path so the published `module-workflow-surface` bundle now expects `25` rows instead of `23`, the `pattern_call` helper mix is `6` `search` / `1` `match` / `6` `fullmatch`, and the new bytes rows are pinned back to `VERBOSE_COMPILE_WORKFLOW_CASES` with their payloads encoded through the existing bytes compile anchor.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated the tracked `reports/correctness/latest.py` publication. The tracked artifact now reads `1395` total / `1395` passed / `0` `unimplemented` across `114` manifests overall, with `module.workflow` at `25` / `25` / `0`, `module.workflow.bytes` at `10` / `10` / `0`, and `module.workflow.pattern_call` at `13` / `13` / `0`; both new bytes verbose helper rows are present in the tracked report.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0731-module-workflow-remaining-positive-bytes-verbose-helpers.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The task-local module-workflow report published `25` total / `25` passed / `0` `unimplemented`.
