# RBR-0777: Publish the module-workflow `Pattern.match` / `Pattern.fullmatch` keyword pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent bound pattern-keyword pair, publishing the exact `Pattern.match(pos=True)` and `Pattern.fullmatch(pos=__index__, endpos=__index__)` workflows for the existing `"abc"` and `b"abc"` anchors before the remaining `Pattern.findall` / `Pattern.finditer` bool-or-indexlike window rows, pattern `split` / `sub` / `subn` keyword rows, compiled-pattern module keyword rows, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `pattern_call` rows:
  - add `workflow-pattern-match-str-bool-pos-keyword`;
  - add `workflow-pattern-fullmatch-bytes-window-indexlike`;
  - keep both rows pinned to the exact direct parity anchors already defined on the shared owner path in `PATTERN_KEYWORD_CALL_CASES`:
    - `pattern-match-bool-pos-keyword-str`: `helper == "match"`, `pattern == "abc"`, `args == ("zabcabc",)`, and `kwargs == {"pos": True}`;
    - `pattern-fullmatch-window-indexlike-bytes`: `helper == "fullmatch"`, `pattern == b"abc"`, `args == (b"zabc",)`, and `kwargs == {"pos": _INDEX_ONE, "endpos": _INDEX_FOUR}`;
  - keep the text-model split explicit: `workflow-pattern-match-str-bool-pos-keyword` stays on `str`, while `workflow-pattern-fullmatch-bytes-window-indexlike` stays on `bytes`; and
  - do not broaden into the remaining `Pattern.findall` / `Pattern.finditer` bool-or-indexlike window rows, pattern `split` / `sub` / `subn` keyword rows, module keyword rows, compiled-pattern module keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `77` total rows instead of `75`;
  - update the owner-path text-model split so the bundle now expects `50` `str` rows and `27` `bytes` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `14` `search` rows, `4` `match` rows, `10` `fullmatch` rows, `2` `findall` rows, and `2` `finditer` rows;
  - keep `module_call` expectations unchanged at `33` rows with the current helper breakdown;
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly these two rows so it now contains eleven published pattern-keyword rows in this order:
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
    - `workflow-pattern-finditer-bytes-window-keyword`
  - extend the focused direct-case alignment assertions so those eleven published rows map back to these direct anchors in the same order:
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
    - `pattern-finditer-window-keyword-bytes`
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1445` total / `1445` passed / `0` `unimplemented` across `114` manifests to `1447` / `1447` / `0` across the same `114` manifests;
  - `module.workflow` moves from `75` / `75` / `0` to `77` / `77` / `0`;
  - `module.workflow.str` moves from `49` / `49` / `0` to `50` / `50` / `0`;
  - `module.workflow.bytes` moves from `26` / `26` / `0` to `27` / `27` / `0`;
  - `module.workflow.pattern_call` moves from `30` / `30` / `0` to `32` / `32` / `0`;
  - `module.workflow.module_call` stays `33` / `33` / `0`; and
  - at least one of the new `workflow-pattern-*keyword*` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0777-module-workflow-pattern-match-fullmatch-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0777` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0776`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - the next-free-id probe across `ops/tasks/**` returned `RBR-0777`.
- Queue this directly after `RBR-0775` on the same `module-workflow-surface` owner path so the next adjacent `Pattern.match` / `Pattern.fullmatch` keyword pair lands before the remaining `Pattern.findall` / `Pattern.finditer` bool-or-indexlike rows, pattern replacement keyword rows, compiled-pattern module keyword rows, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-match-bool-pos-keyword-str` and `pattern-fullmatch-window-indexlike-bytes` in `PATTERN_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword_argument_calls_match_cpython and (pattern-match-bool-pos-keyword-str or pattern-fullmatch-window-indexlike-bytes)'` passed in this run (`4 passed, 707 deselected`);
  - direct publication probes in this run confirmed both `workflow-pattern-match-str-bool-pos-keyword` and `workflow-pattern-fullmatch-bytes-window-indexlike` are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent `Pattern.match(pos=...)` and `Pattern.fullmatch(pos=..., endpos=...)` representative rows, leaving this bool-plus-`__index__` pair as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
