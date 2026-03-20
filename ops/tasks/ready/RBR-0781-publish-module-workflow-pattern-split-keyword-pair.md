# RBR-0781: Publish the module-workflow `Pattern.split` keyword pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent pattern-keyword pair, publishing the exact `Pattern.split(maxsplit=1)` and `Pattern.split(maxsplit=__index__)` workflows for the existing `"abc"` anchor before the remaining pattern `sub` / `subn` keyword rows, compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-split-str-maxsplit-keyword`;
  - add `workflow-pattern-split-str-maxsplit-indexlike`;
  - keep both rows pinned to the exact direct parity anchors already defined on the shared owner path in `PATTERN_KEYWORD_CALL_CASES`:
    - `pattern-split-maxsplit-keyword-str`: `helper == "split"`, `pattern == "abc"`, `args == ("zabczabc",)`, and `kwargs == {"maxsplit": 1}`;
    - `pattern-split-maxsplit-indexlike-str`: `helper == "split"`, `pattern == "abc"`, `args == ("zabcabcabc",)`, and `kwargs == {"maxsplit": _INDEX_TWO}`;
  - keep both rows on `str`; and
  - do not broaden into the remaining pattern `sub` / `subn` keyword rows, module keyword rows, compiled-pattern module keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `83` total rows instead of `81`;
  - update the owner-path text-model split so the bundle now expects `54` `str` rows and `29` `bytes` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `14` `search` rows, `4` `match` rows, `10` `fullmatch` rows, `4` `findall` rows, `4` `finditer` rows, and `2` `split` rows;
  - keep `module_call` expectations unchanged at `33` rows with the current helper breakdown;
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly these two rows so it now contains seventeen published pattern-keyword rows in this order:
    - `workflow-pattern-search-str-pos-keyword`
    - `workflow-pattern-search-str-bool-endpos-keyword`
    - `workflow-pattern-search-bytes-endpos-keyword`
    - `workflow-pattern-search-str-pos-indexlike`
    - `workflow-pattern-search-bytes-endpos-indexlike`
    - `workflow-pattern-match-str-pos-keyword`
    - `workflow-pattern-match-str-bool-pos-keyword`
    - `workflow-pattern-fullmatch-bytes-window-keyword`
    - `workflow-pattern-fullmatch-bytes-window-indexlike`
    - `workflow-pattern-findall-str-window-keyword`
    - `workflow-pattern-findall-str-window-indexlike`
    - `workflow-pattern-findall-str-bool-window-keyword`
    - `workflow-pattern-finditer-bytes-window-keyword`
    - `workflow-pattern-finditer-bytes-window-indexlike`
    - `workflow-pattern-finditer-bytes-bool-window-keyword`
    - `workflow-pattern-split-str-maxsplit-keyword`
    - `workflow-pattern-split-str-maxsplit-indexlike`
  - extend the focused direct-case alignment assertions so those seventeen published rows map back to these direct anchors in the same order:
    - `pattern-search-pos-keyword-str`
    - `pattern-search-bool-endpos-keyword-str`
    - `pattern-search-endpos-keyword-bytes`
    - `pattern-search-pos-indexlike-str`
    - `pattern-search-endpos-indexlike-bytes`
    - `pattern-match-pos-keyword-str`
    - `pattern-match-bool-pos-keyword-str`
    - `pattern-fullmatch-window-keyword-bytes`
    - `pattern-fullmatch-window-indexlike-bytes`
    - `pattern-findall-window-keyword-str`
    - `pattern-findall-window-indexlike-str`
    - `pattern-findall-bool-window-keyword-str`
    - `pattern-finditer-window-keyword-bytes`
    - `pattern-finditer-window-indexlike-bytes`
    - `pattern-finditer-bool-window-keyword-bytes`
    - `pattern-split-maxsplit-keyword-str`
    - `pattern-split-maxsplit-indexlike-str`
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1451` total / `1451` passed / `0` `unimplemented` across `114` manifests to `1453` / `1453` / `0` across the same `114` manifests;
  - `module.workflow` moves from `81` / `81` / `0` to `83` / `83` / `0`;
  - `module.workflow.str` moves from `52` / `52` / `0` to `54` / `54` / `0`;
  - `module.workflow.bytes` stays `29` / `29` / `0`;
  - `module.workflow.pattern_call` moves from `36` / `36` / `0` to `38` / `38` / `0`;
  - `module.workflow.module_call` stays `33` / `33` / `0`; and
  - at least one of the new `workflow-pattern-split-*` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0781-module-workflow-pattern-split-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0781` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0780`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - the next-free-id probe across `ops/tasks/**` plus reserved ids in `ops/state/backlog.md` and `ops/state/current_status.md` returned `RBR-0781`.
- Queue this directly after `RBR-0779` on the same `module-workflow-surface` owner path so the remaining adjacent `Pattern.split(maxsplit=...)` pair lands before the pattern `sub` / `subn` keyword rows, compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-split-maxsplit-keyword-str` and `pattern-split-maxsplit-indexlike-str` in `PATTERN_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword_argument_calls_match_cpython and (pattern-split-maxsplit-keyword-str or pattern-split-maxsplit-indexlike-str)'` passed in this run (`4 passed, 715 deselected`);
  - direct publication probes in this run confirmed both `workflow-pattern-split-str-maxsplit-keyword` and `workflow-pattern-split-str-maxsplit-indexlike` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent `Pattern.findall` / `Pattern.finditer` keyword-window rows, leaving this `Pattern.split(maxsplit=...)` pair as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
