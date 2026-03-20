# RBR-0784: Publish the module-workflow compiled-pattern `split` keyword pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module keyword pair, publishing the exact `rebar.split(compiled_pattern, ..., maxsplit=1)` and `rebar.split(compiled_pattern, ..., maxsplit=__index__)` workflows for the existing `"abc"` and `b"abc"` anchors before compiled-pattern module `sub` / `subn` keyword rows, compiled-pattern keyword-error rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-split-maxsplit-keyword-str-compiled-pattern`;
  - add `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern`;
  - keep both rows pinned to the exact direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES`:
    - `compiled-pattern-split-maxsplit-keyword-str`: `helper == "split"`, `pattern == "abc"`, `args == ("zabczabc",)`, and `kwargs == {"maxsplit": 1}`;
    - `compiled-pattern-split-maxsplit-indexlike-bytes`: `helper == "split"`, `pattern == b"abc"`, `args == (b"zabcabcabc",)`, and `kwargs == {"maxsplit": _INDEX_TWO}`;
  - keep the compiled-pattern routing explicit by setting `use_compiled_pattern` on both rows;
  - keep the text-model split explicit: `workflow-module-split-maxsplit-keyword-str-compiled-pattern` stays on `str`, while `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern` stays on `bytes`; and
  - do not broaden into compiled-pattern module `sub` / `subn` keyword rows, compiled-pattern keyword-error rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `89` total rows instead of `87`;
  - update the owner-path text-model split so the bundle now expects `57` `str` rows and `32` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `6` `search` rows, `4` `match` rows, `5` `fullmatch` rows, `6` `split` rows, `1` `findall` row, `1` `finditer` row, `6` `sub` rows, `4` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains sixteen rows, inserting the two new fixture ids immediately after `workflow-module-split-str-compiled-pattern` and before `workflow-module-findall-bytes-compiled-pattern`;
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise inserts `compiled-pattern-split-maxsplit-keyword-str` and `compiled-pattern-split-maxsplit-indexlike-bytes` immediately after `compiled-pattern-split-str-maxsplit` and before `compiled-pattern-findall-bytes`; and
  - teach the shared compiled-pattern publication contract to compare the two new rows by normalized keyword signature so the existing owner-path selector stays honest without dropping back to a second manifest or a detached keyword-only publication path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1457` total / `1457` passed / `0` `unimplemented` across `114` manifests to `1459` / `1459` / `0` across the same `114` manifests;
  - `module.workflow` moves from `87` / `87` / `0` to `89` / `89` / `0`;
  - `module.workflow.str` moves from `56` / `56` / `0` to `57` / `57` / `0`;
  - `module.workflow.bytes` moves from `31` / `31` / `0` to `32` / `32` / `0`;
  - `module.workflow.module_call` moves from `33` / `33` / `0` to `35` / `35` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new `workflow-module-split-maxsplit-*compiled-pattern` rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0784-module-workflow-compiled-pattern-split-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern keyword publication file.

## Notes
- `RBR-0784` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0783`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `rg -n "\\bRBR-0784\\b" ops/state/current_status.md ops/state/backlog.md ops/tasks` returned no active reservation for this id in this run.
- Queue this directly after `RBR-0783` on the same `module-workflow-surface` owner path so the adjacent compiled-pattern `split(maxsplit=...)` keyword pair lands before compiled-pattern module `sub` / `subn` keyword rows, compiled-pattern keyword-error rows, benchmark catch-up, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-split-maxsplit-keyword-str` and `compiled-pattern-split-maxsplit-indexlike-bytes` in `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython` passed in this run (`12 passed`);
  - direct publication probes in this run confirmed both `workflow-module-split-maxsplit-keyword-str-compiled-pattern` and `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent non-keyword compiled-pattern row `workflow-module-split-str-compiled-pattern`, leaving this compiled-pattern `split(maxsplit=...)` keyword pair as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
