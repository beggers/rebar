# RBR-0734: Publish the module-workflow bytes verbose compiled-pattern module-helper pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the module-workflow correctness frontier with the first bounded `bytes` module-level `search()` / `fullmatch()` helper pair that accepts a compiled pattern, so the existing `module-workflow-surface` owner path can start publishing compiled-pattern module-helper behavior without forking another manifest or leaving this adjacent verbose slice stranded in direct pytest coverage only.

## Deliverables
- `python/rebar_harness/correctness.py`
- `tests/python/test_fixture_parity_support_contract.py`
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `python/rebar_harness/correctness.py` and `tests/python/test_fixture_parity_support_contract.py` extend the existing Python fixture path just enough to publish compiled-pattern module-helper workflows on ordinary `module_call` rows:
  - add one reusable case-level switch on `FixtureCase` for `module_call` rows that tells the observer to compile `case.pattern` with `case.flags` and pass the resulting compiled pattern as the first helper argument before the existing serialized `args`;
  - keep ordinary raw-pattern `module_call` rows unchanged, including the existing `module-workflow-surface` `escape()` rows and every non-module-workflow manifest already published in `reports/correctness/latest.py`;
  - keep the fixture/report path standard-looking: do not add a second manifest for this pair, a detached report path, or a one-off verbose-only operation name.
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two `module_call` rows:
  - add `workflow-module-search-bytes-verbose-regression-compiled-pattern` and `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`;
  - keep both rows pinned to the exact shared verbose regression pattern and bytes compile anchor already published on `module-workflow-surface`:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "bytes"` for both rows;
    - mark both rows to call the module helper with a compiled pattern rather than the raw pattern string;
    - `helper == "search"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "prefix\\nENV_VAR=ABCD\\nsuffix"}]` for `workflow-module-search-bytes-verbose-regression-compiled-pattern`; and
    - `helper == "fullmatch"` with `args == [{"type": "bytes", "encoding": "latin-1", "value": "ENV_VAR = 123"}]` for `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`;
  - do not broaden into the remaining verbose bytes direct-case table, non-verbose compiled-pattern helpers, keyword-argument helpers, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing owner path without forking another verbose-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `29` total rows instead of `27`;
  - update the shared `module_call` breakdown so the owner path now expects `2` `escape` rows plus `1` compiled-pattern `search` row and `1` compiled-pattern `fullmatch` row;
  - reuse `VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES` as the source of truth for the new published rows and assert that the fixture-backed publication stays pinned to those exact direct parity cases instead of inventing another bytes-specific scenario table.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1397` total / `1397` passed / `0` `unimplemented` across `114` manifests to `1399` / `1399` / `0` across the same `114` manifests;
  - `module.workflow` moves from `27` / `27` / `0` to `29` / `29` / `0`;
  - `module.workflow.bytes` moves from `12` / `12` / `0` to `14` / `14` / `0`;
  - `module.workflow.module_call` moves from `2` / `2` / `0` to `4` / `4` / `0`; and
  - both new compiled-pattern module-helper rows are visible in the tracked scorecard as representative `module-workflow-surface` cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_fixture_parity_support_contract.py tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0734-module-workflow-bytes-verbose-compiled-pattern-module-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task on the existing backend-parameterized Python correctness path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern publication file for this pair.
- Keep any fixture-path extension reusable for later compiled-pattern module-helper publication instead of introducing a verbose-only special case.
- Do not change benchmark manifests, benchmark reports, README text, or harness files outside the correctness publication path in this run.

## Notes
- `RBR-0734` is the next tail task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0733`, `ops/tasks/ready/` is empty at the start of this run, and the only files under `ops/tasks/in_progress/` and `ops/tasks/blocked/` are `.gitkeep`; and
  - older missing ids exist in historical ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after `RBR-0733` so the same module-workflow bytes verbose owner path starts publishing its adjacent compiled-pattern module-helper slice instead of pausing for another family.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `ops/tasks/done/RBR-0733-publish-module-workflow-bytes-verbose-miss-path-helper-pair.md` closed the remaining bytes verbose `pattern_call` miss rows and left no real ready, blocked, or in-progress feature task behind it;
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact direct parity anchor `VERBOSE_BYTES_COMPILED_PATTERN_MODULE_HELPER_CASES` on the same verbose bytes family, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'preserve_verbose_bytes_compiled_pattern_identity_like_cpython'` passes with `16 passed`;
  - a direct runtime probe in this run confirmed that `rebar.search(compiled_pattern, b"prefix\\nENV_VAR=ABCD\\nsuffix")` and `rebar.fullmatch(compiled_pattern, b"ENV_VAR = 123")` already match CPython with the same spans on the anchored bytes verbose pattern; and
  - `module-workflow-surface` currently publishes only the `escape()` `module_call` rows, so the next adjacent owner-path publication slice is the first bounded compiled-pattern module-helper pair rather than another compile row or benchmark catch-up pass.
