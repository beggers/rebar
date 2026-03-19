# RBR-0722: Publish the module-workflow verbose pattern-helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-19

## Goal
- Reopen the module-workflow correctness frontier with the exact verbose compiled-pattern `search()` / `fullmatch()` pair that already exists on the shared owner path, so the newly drained multiline-bytes compile family rolls forward on the same regression spelling before bytes helper gaps or benchmark expansion broaden this module-workflow branch.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-search-str-verbose-regression` and `workflow-pattern-fullmatch-str-verbose-regression` beside the existing module-workflow regression compile rows;
  - keep the exact shared verbose regression pattern anchored to the existing module-workflow compile family instead of inventing another pattern family:
    - `pattern == "^ (?P<key>[A-Z_]+) \\s* = \\s* (?:[A-Z]{2,4}+|\\d{2,3}) $"`;
    - `flags == 72` (`MULTILINE | VERBOSE`);
    - `text_model == "str"` for both new rows;
    - `helper == "search"` with `args == ["prefix\nENV_VAR=ABCD\nsuffix"]` for `workflow-pattern-search-str-verbose-regression`; and
    - `helper == "fullmatch"` with `args == ["ENV_VAR = 123"]` for `workflow-pattern-fullmatch-str-verbose-regression`;
  - do not broaden into bytes siblings, miss-path rows, module-helper rows, cache-state variants, or another workflow family in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without forking another regression-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `17` total rows instead of `15`;
  - update the pattern-call breakdown so the shared owner path now expects `2` `search` rows, `1` `match` row, and `2` `fullmatch` rows on the published manifest;
  - keep the existing `VERBOSE_COMPILE_WORKFLOW_CASES` and their direct parity assertions as the source of truth for this exact helper pair instead of duplicating another file-local scenario table; and
  - do not add a new parity module, a detached regression helper fixture, or bytes helper expectations in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1385` total / `1385` passed / `0` `unimplemented` across `114` manifests to `1387` / `1387` / `0` across the same `114` manifests;
  - `module.workflow` moves from `15` total / `15` passed / `0` `unimplemented` to `17` / `17` / `0`;
  - `module.workflow.str` moves from `9` total / `9` passed / `0` `unimplemented` to `11` / `11` / `0`; and
  - `module.workflow.pattern_call` moves from `3` total / `3` passed / `0` `unimplemented` to `5` / `5` / `0`, with both new regression helper rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0722-module-workflow-verbose-patterns.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, or benchmark reports in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached regression workflow helper just for this pair.
- Keep any later bytes-helper follow-on or benchmark catch-up on the existing module-workflow / Python-path owner surfaces instead of inventing a second family.

## Notes
- `RBR-0722` is the next available feature task id in the current checkout; `RBR-0721` is already occupied by the done architecture cleanup task in `ops/tasks/done/`, and `rg -n "RBR-0722" ops/tasks/ready ops/tasks/in_progress ops/tasks/done ops/tasks/blocked ops/state/backlog.md ops/state/current_status.md` returned no matches during this planning run.
- Queue this directly after the drained `RBR-0720` head so the module-workflow regression family stays on the existing correctness owner path after the multiline-bytes compile benchmark catch-up closes.
- 2026-03-19 feature-planning probes confirm this follow-on is concrete from tracked frontier evidence:
  - `ops/tasks/done/RBR-0720-module-workflow-multiline-bytes-compile-benchmark-catch-up.md` closed the last queued compile follow-on on the shared module-workflow regression family and left the feature queue empty;
  - `tests/python/test_module_workflow_parity_suite.py` already defines the exact `VERBOSE_COMPILE_WORKFLOW_CASES` for the shared verbose regression pattern and verifies `search("prefix\nENV_VAR=ABCD\nsuffix")` plus `fullmatch("ENV_VAR = 123")` through the compiled-pattern owner path;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes only the compile/cache/escape/literal pattern workflow rows on `module-workflow-surface`, with no published verbose regression `pattern_call` companions for that same pattern;
  - `tests/conformance/test_combined_correctness_scorecards.py` currently names `workflow-pattern-search-str` and `workflow-pattern-fullmatch-bytes` as the representative published `pattern_call` rows for `module-workflow-surface`, but not the already-exercised verbose regression pair; and
  - `reports/correctness/latest.py` currently reports `1385` total / `1385` passed / `0` `unimplemented` across `114` manifests, with `module.workflow.pattern_call` at `3` total / `3` passed / `0` `unimplemented`, so this slice reopens the tracked frontier through adjacent published-owner coverage rather than a new family.

## Completion
- 2026-03-19: Added `workflow-pattern-search-str-verbose-regression` and `workflow-pattern-fullmatch-str-verbose-regression` to `tests/conformance/fixtures/module_workflow_surface.py`, keeping the exact shared verbose regression pattern on the existing `module-workflow-surface` manifest with `flags == 72`, `text_model == "str"`, and the bounded compiled-pattern `search()` / `fullmatch()` helper calls requested by this task.
- Updated `tests/python/test_module_workflow_parity_suite.py` on the existing owner path so the published module-workflow bundle now expects `17` rows instead of `15`, the `pattern_call` helper mix is `2` `search` / `1` `match` / `2` `fullmatch`, the manifest order is pinned directly against the selected case inventory, and the existing `VERBOSE_COMPILE_WORKFLOW_CASES` now exercise the published `fullmatch("ENV_VAR = 123")` regression sample instead of drifting from the manifest.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated the tracked `reports/correctness/latest.py` publication. After publication, the tracked artifact reads `1387` total / `1387` passed / `0` `unimplemented` across `114` manifests overall, `module.workflow` is `17` / `17` / `0`, `module.workflow.str` is `11` / `11` / `0`, and `module.workflow.pattern_call` is `5` / `5` / `0`, with both new verbose regression helper rows present in the tracked report.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0722-module-workflow-verbose-patterns.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`. The narrow manifest report published `17` total / `17` passed / `0` `unimplemented`.
