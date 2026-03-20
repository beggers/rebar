# RBR-0738: Publish the module-workflow compiled-pattern collection helper pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the `module-workflow-surface` correctness frontier with the first bounded compiled-pattern collection helper pair, so the existing owner path starts publishing adjacent `split()` / `findall()` module-helper behavior without forking another manifest, jumping into replacement helpers, or broadening into benchmark catch-up.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-split-str-compiled-pattern` and `workflow-module-findall-bytes-compiled-pattern`;
  - keep both rows pinned to the exact adjacent direct parity cases already defined on the shared owner path:
    - `compiled-pattern-split-str-maxsplit`: `pattern == "abc"`, default zero flags, `helper == "split"`, `use_compiled_pattern == True`, and `args == ["zzabczzabc", 1]`;
    - `compiled-pattern-findall-bytes`: `pattern == "abc"`, `text_model == "bytes"`, default zero flags, `helper == "findall"`, `use_compiled_pattern == True`, and `args == [{"type": "bytes", "encoding": "latin-1", "value": "zabcabc"}]`;
  - do not broaden into the remaining literal-bytes compiled-pattern `fullmatch()` singleton, `finditer()` / `sub()` / `subn()` helpers, compiled-pattern type-error rows, keyword-argument helpers, or benchmark rows in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another compiled-pattern-specific suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `33` total rows instead of `31`;
  - update the shared `module_call` breakdown so the owner path now expects `2` `search` rows, `1` `match` row, `1` `fullmatch` row, `1` `split` row, `1` `findall` row, and `2` `escape` rows;
  - keep the new rows pinned to the exact direct parity anchors `compiled-pattern-split-str-maxsplit` and `compiled-pattern-findall-bytes` from `COMPILED_PATTERN_MODULE_HELPER_CASES` instead of inventing another literal-only scenario table; and
  - keep the module-workflow direct-test bucket coverage honest by expanding the published compiled-module-helper ownership to include the new collection-helper pair alongside the already published search/match/fullmatch rows.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1401` total / `1401` passed / `0` `unimplemented` across `114` manifests to `1403` / `1403` / `0` across the same `114` manifests;
  - `module.workflow` moves from `31` / `31` / `0` to `33` / `33` / `0`;
  - `module.workflow.str` moves from `17` / `17` / `0` to `18` / `18` / `0`;
  - `module.workflow.bytes` moves from `14` / `14` / `0` to `15` / `15` / `0`; and
  - `module.workflow.module_call` moves from `6` / `6` / `0` to `8` / `8` / `0`, with both new compiled-pattern collection-helper rows visible in the tracked scorecard.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0738-module-workflow-compiled-pattern-collection-helpers.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust or Python implementation code, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern module-helper publication file.

## Notes
- `RBR-0738` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0737`;
  - no newer `feature-implementation` task is ready, in progress, or blocked; and
  - older missing ids exist in historical ranges, but none are still named as the live feature frontier in tracked queue/state files.
- Queue this directly after `RBR-0736` so the same compiled-pattern module-helper family continues on the existing `module-workflow-surface` owner path instead of jumping to replacement helpers, keyword arguments, or another manifest.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-split-str-maxsplit` and `compiled-pattern-findall-bytes` in `COMPILED_PATTERN_MODULE_HELPER_CASES`;
  - a direct runtime probe in this run confirmed that `rebar.split(rebar.compile("abc"), "zzabczzabc", 1)` returns `["zz", "zzabc"]` and `rebar.findall(rebar.compile(b"abc"), b"zabcabc")` returns `[b"abc", b"abc"]`, matching CPython on the same helper calls;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes compiled-pattern `module_call` rows for search/match/fullmatch plus `escape()`, but no compiled-pattern collection-helper rows, leaving this pair as the next bounded adjacent publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Added only the requested `module_call` rows to `tests/conformance/fixtures/module_workflow_surface.py`: `workflow-module-split-str-compiled-pattern` and `workflow-module-findall-bytes-compiled-pattern`, pinned to the existing direct anchors `compiled-pattern-split-str-maxsplit` and `compiled-pattern-findall-bytes` with the task’s exact args, text models, zero-flag path, and `use_compiled_pattern == True` contract.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the existing `module-workflow-surface` owner path now expects `33` published rows, a `module_call` helper breakdown of `search == 2`, `match == 1`, `fullmatch == 1`, `split == 1`, `findall == 1`, and `escape == 2`, and compiled-module-helper ownership that now includes the published collection-helper pair alongside the previously published search/match/fullmatch rows.
- Updated `tests/conformance/test_combined_correctness_scorecards.py` and regenerated `reports/correctness/latest.py`. Reading the tracked report artifact shows `1403` total / `1403` passed / `0` `unimplemented` across `114` manifests, with `module.workflow` at `33` / `33` / `0`, `module.workflow.str` at `18` / `18` / `0`, `module.workflow.bytes` at `15` / `15` / `0`, and `module.workflow.module_call` at `8` / `8` / `0`; both new compiled-pattern collection-helper rows are present in the tracked scorecard with `comparison == "pass"`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0738-module-workflow-compiled-pattern-collection-helpers.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`. The task-local module-workflow report published `33` total / `33` passed / `0` `unimplemented`.
