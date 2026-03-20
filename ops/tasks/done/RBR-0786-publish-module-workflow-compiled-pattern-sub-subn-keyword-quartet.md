# RBR-0786: Publish the module-workflow compiled-pattern `sub` / `subn` keyword quartet

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent compiled-pattern module keyword quartet, publishing the exact `rebar.sub(compiled_pattern, ..., count=1)`, `rebar.sub(compiled_pattern, ..., count=__index__)`, `rebar.subn(compiled_pattern, ..., count=1)`, and `rebar.subn(compiled_pattern, ..., count=__index__)` workflows for the existing `"abc"` and `b"abc"` anchors before compiled-pattern keyword-error rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only four new `module_call` rows:
  - add `workflow-module-sub-count-keyword-str-compiled-pattern`;
  - add `workflow-module-sub-count-indexlike-bytes-compiled-pattern`;
  - add `workflow-module-subn-count-keyword-bytes-compiled-pattern`;
  - add `workflow-module-subn-count-indexlike-str-compiled-pattern`;
  - keep all four rows pinned to the exact direct parity anchors already defined on the shared owner path in `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES`:
    - `compiled-pattern-sub-count-keyword-str`: `helper == "sub"`, `pattern == "abc"`, `args == ("x", "abcabc")`, and `kwargs == {"count": 1}`;
    - `compiled-pattern-sub-count-indexlike-bytes`: `helper == "sub"`, `pattern == b"abc"`, `args == (b"x", b"abcabcabc")`, and `kwargs == {"count": _INDEX_TWO}`;
    - `compiled-pattern-subn-count-keyword-bytes`: `helper == "subn"`, `pattern == b"abc"`, `args == (b"x", b"abcabc")`, and `kwargs == {"count": 1}`;
    - `compiled-pattern-subn-count-indexlike-str`: `helper == "subn"`, `pattern == "abc"`, `args == ("x", "abcabcabc")`, and `kwargs == {"count": _INDEX_TWO}`;
  - keep the compiled-pattern routing explicit by setting `use_compiled_pattern` on all four rows;
  - keep the text-model split explicit: the `workflow-module-sub-count-keyword-str-compiled-pattern` and `workflow-module-subn-count-indexlike-str-compiled-pattern` rows stay on `str`, while the `workflow-module-sub-count-indexlike-bytes-compiled-pattern` and `workflow-module-subn-count-keyword-bytes-compiled-pattern` rows stay on `bytes`; and
  - do not broaden into compiled-pattern keyword-error rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest, detached selector table, or second compiled-pattern owner path:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `93` total rows instead of `89`;
  - update the owner-path text-model split so the bundle now expects `59` `str` rows and `34` `bytes` rows;
  - keep `pattern_call` expectations unchanged at `42` rows with the current helper breakdown;
  - update the shared `module_call` helper breakdown so the owner path now expects `6` `search` rows, `4` `match` rows, `5` `fullmatch` rows, `6` `split` rows, `1` `findall` row, `1` `finditer` row, `8` `sub` rows, `6` `subn` rows, and `2` `escape` rows;
  - extend the published compiled-pattern owner-path assertions so `PUBLISHED_COMPILED_PATTERN_MODULE_HELPER_CASES` now contains twenty rows, inserting the four new fixture ids adjacent to the existing compiled-pattern `sub` / `subn` rows so the published order becomes:
    - `workflow-module-search-str-compiled-pattern`
    - `workflow-module-match-str-compiled-pattern`
    - `workflow-module-search-str-bounded-wildcard-ignorecase-compiled-pattern`
    - `workflow-module-match-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-fullmatch-str-bounded-wildcard-compiled-pattern`
    - `workflow-module-search-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-fullmatch-bytes-verbose-regression-compiled-pattern`
    - `workflow-module-split-str-compiled-pattern`
    - `workflow-module-split-maxsplit-keyword-str-compiled-pattern`
    - `workflow-module-split-maxsplit-indexlike-bytes-compiled-pattern`
    - `workflow-module-findall-bytes-compiled-pattern`
    - `workflow-module-finditer-str-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern`
    - `workflow-module-sub-count-keyword-str-compiled-pattern`
    - `workflow-module-sub-count-indexlike-bytes-compiled-pattern`
    - `workflow-module-sub-str-compiled-pattern-on-bytes-string`
    - `workflow-module-subn-bytes-compiled-pattern`
    - `workflow-module-subn-count-keyword-bytes-compiled-pattern`
    - `workflow-module-subn-count-indexlike-str-compiled-pattern`
    - `workflow-module-subn-bytes-compiled-pattern-on-str-string`
  - extend the compiled-pattern direct-case alignment so the published direct-anchor sequence likewise becomes:
    - `compiled-pattern-search-str`
    - `compiled-pattern-match-str`
    - `compiled-module-search-ignorecase-bounded-hit`
    - `compiled-module-match-bounded-hit`
    - `compiled-module-fullmatch-bounded-hit`
    - `compiled-pattern-search-bytes-verbose-regression`
    - `compiled-pattern-fullmatch-bytes-verbose-regression`
    - `compiled-pattern-split-str-maxsplit`
    - `compiled-pattern-split-maxsplit-keyword-str`
    - `compiled-pattern-split-maxsplit-indexlike-bytes`
    - `compiled-pattern-findall-bytes`
    - `compiled-pattern-finditer-str`
    - `compiled-pattern-sub-str-count`
    - `compiled-pattern-sub-count-keyword-str`
    - `compiled-pattern-sub-count-indexlike-bytes`
    - `compiled-pattern-sub-str-on-bytes-string`
    - `compiled-pattern-subn-bytes-count`
    - `compiled-pattern-subn-count-keyword-bytes`
    - `compiled-pattern-subn-count-indexlike-str`
    - `compiled-pattern-subn-bytes-on-str-string`
  - keep the existing normalized keyword-signature comparison path for compiled-pattern module helper rows instead of adding another helper-specific publication path; and
  - keep the raw module keyword helper rows, module keyword-error rows, pattern keyword rows, and benchmark-oriented assertions unchanged in this run.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1459` total / `1459` passed / `0` `unimplemented` across `114` manifests to `1463` / `1463` / `0` across the same `114` manifests;
  - `module.workflow` moves from `89` / `89` / `0` to `93` / `93` / `0`;
  - `module.workflow.str` moves from `57` / `57` / `0` to `59` / `59` / `0`;
  - `module.workflow.bytes` moves from `32` / `32` / `0` to `34` / `34` / `0`;
  - `module.workflow.module_call` moves from `35` / `35` / `0` to `39` / `39` / `0`;
  - `module.workflow.pattern_call` stays `42` / `42` / `0`; and
  - at least one of the new `workflow-module-sub-count-*compiled-pattern` or `workflow-module-subn-count-*compiled-pattern` rows is visible in the tracked scorecard as a representative `module-workflow-surface` compiled-pattern module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0786-module-workflow-compiled-pattern-sub-subn-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached compiled-pattern keyword publication file.

## Notes
- `RBR-0786` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0785`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `rg -n 'RBR-0786' ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no active reservation for this id in this run.
- Queue this directly after `RBR-0784` on the same `module-workflow-surface` owner path so the adjacent compiled-pattern replacement keyword quartet lands before compiled-pattern keyword-error rows, benchmark catch-up, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `compiled-pattern-sub-count-keyword-str`, `compiled-pattern-sub-count-indexlike-bytes`, `compiled-pattern-subn-count-keyword-bytes`, and `compiled-pattern-subn-count-indexlike-str` in `COMPILED_PATTERN_MODULE_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py::test_compiled_pattern_module_keyword_argument_calls_match_cpython` passed in this run (`12 passed`);
  - direct publication probes in this run confirmed the four new workflow ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent compiled-pattern `split(maxsplit=...)` keyword pair and the plain compiled-pattern `sub` / `subn` helper rows, leaving this `sub` / `subn` keyword quartet as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- Added the four adjacent compiled-pattern module-call rows on the existing `module-workflow-surface` owner path: `workflow-module-sub-count-keyword-str-compiled-pattern`, `workflow-module-sub-count-indexlike-bytes-compiled-pattern`, `workflow-module-subn-count-keyword-bytes-compiled-pattern`, and `workflow-module-subn-count-indexlike-str-compiled-pattern`.
- Updated the shared parity-suite publication contract to `93` owner-path rows with a `59`/`34` `str`/`bytes` split, `39` published `module_call` rows, `8` `sub` rows, `6` `subn` rows, and a `20`-row compiled-pattern module publication sequence while keeping `pattern_call` at `42`.
- Extended the shared compiled-pattern publication alignment and representative scorecard coverage to include the four direct anchors `compiled-pattern-sub-count-keyword-str`, `compiled-pattern-sub-count-indexlike-bytes`, `compiled-pattern-subn-count-keyword-bytes`, and `compiled-pattern-subn-count-indexlike-str` without adding a detached compiled-pattern keyword publication path.
- Regenerated the tracked published correctness scorecard at `reports/correctness/latest.py`; the tracked artifact now reports `1463` total / `1463` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `93/93/0`, `module.workflow.str` at `59/59/0`, `module.workflow.bytes` at `34/34/0`, `module.workflow.module_call` at `39/39/0`, and `module.workflow.pattern_call` unchanged at `42/42/0`. The tracked report includes all four new compiled-pattern `sub` / `subn` keyword rows.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0786-module-workflow-compiled-pattern-sub-subn-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
