# RBR-0783: Publish the module-workflow `Pattern.sub` / `Pattern.subn` keyword quartet

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent pattern-keyword quartet, publishing the exact `Pattern.sub(count=1)`, `Pattern.sub(count=__index__)`, `Pattern.subn(count=1)`, and `Pattern.subn(count=__index__)` workflows for the existing `b"abc"` and `"abc"` anchors before compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only four new `pattern_call` rows:
  - add `workflow-pattern-sub-count-keyword-bytes`;
  - add `workflow-pattern-sub-count-indexlike-bytes`;
  - add `workflow-pattern-subn-count-keyword-str`;
  - add `workflow-pattern-subn-count-indexlike-str`;
  - keep all four rows pinned to the exact direct parity anchors already defined on the shared owner path in `PATTERN_KEYWORD_CALL_CASES`:
    - `pattern-sub-count-keyword-bytes`: `helper == "sub"`, `pattern == b"abc"`, `args == (b"x", b"abcabc")`, and `kwargs == {"count": 1}`;
    - `pattern-sub-count-indexlike-bytes`: `helper == "sub"`, `pattern == b"abc"`, `args == (b"x", b"abcabcabc")`, and `kwargs == {"count": _INDEX_TWO}`;
    - `pattern-subn-count-keyword-str`: `helper == "subn"`, `pattern == "abc"`, `args == ("x", "abcabc")`, and `kwargs == {"count": 1}`;
    - `pattern-subn-count-indexlike-str`: `helper == "subn"`, `pattern == "abc"`, `args == ("x", "abcabcabc")`, and `kwargs == {"count": _INDEX_TWO}`;
  - keep the text-model split explicit: both `workflow-pattern-sub-*` rows stay on `bytes`, while both `workflow-pattern-subn-*` rows stay on `str`; and
  - do not broaden into compiled-pattern module keyword rows, benchmark manifests, benchmark reports, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `87` total rows instead of `83`;
  - update the owner-path text-model split so the bundle now expects `56` `str` rows and `31` `bytes` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `14` `search` rows, `4` `match` rows, `10` `fullmatch` rows, `4` `findall` rows, `4` `finditer` rows, `2` `split` rows, `2` `sub` rows, and `2` `subn` rows;
  - keep `module_call` expectations unchanged at `33` rows with the current helper breakdown;
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly these four rows so it now contains twenty-one published pattern-keyword rows in this order:
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
    - `workflow-pattern-sub-count-keyword-bytes`
    - `workflow-pattern-sub-count-indexlike-bytes`
    - `workflow-pattern-subn-count-keyword-str`
    - `workflow-pattern-subn-count-indexlike-str`
  - extend the focused direct-case alignment assertions so those twenty-one published rows map back to these direct anchors in the same order:
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
    - `pattern-sub-count-keyword-bytes`
    - `pattern-sub-count-indexlike-bytes`
    - `pattern-subn-count-keyword-str`
    - `pattern-subn-count-indexlike-str`
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1453` total / `1453` passed / `0` `unimplemented` across `114` manifests to `1457` / `1457` / `0` across the same `114` manifests;
  - `module.workflow` moves from `83` / `83` / `0` to `87` / `87` / `0`;
  - `module.workflow.str` moves from `54` / `54` / `0` to `56` / `56` / `0`;
  - `module.workflow.bytes` moves from `29` / `29` / `0` to `31` / `31` / `0`;
  - `module.workflow.pattern_call` moves from `38` / `38` / `0` to `42` / `42` / `0`;
  - `module.workflow.module_call` stays `33` / `33` / `0`; and
  - at least one of the new `workflow-pattern-sub-*` or `workflow-pattern-subn-*` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0783-module-workflow-pattern-sub-subn-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0783` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0782`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run; and
  - `rg -n "RBR-0783" ops/tasks ops/state/current_status.md ops/state/backlog.md` returned no matches in this run.
- Queue this directly after `RBR-0781` on the same `module-workflow-surface` owner path so the remaining adjacent pattern replacement keyword quartet lands before compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-sub-count-keyword-bytes`, `pattern-sub-count-indexlike-bytes`, `pattern-subn-count-keyword-str`, and `pattern-subn-count-indexlike-str` in `PATTERN_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword_argument_calls_match_cpython and (pattern-sub-count-keyword-bytes or pattern-sub-count-indexlike-bytes or pattern-subn-count-keyword-str or pattern-subn-count-indexlike-str)'` passed in this run (`8 passed, 713 deselected`);
  - direct publication probes in this run confirmed the four new workflow ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent `Pattern.split(maxsplit=...)` keyword pair, leaving this `Pattern.sub` / `Pattern.subn` quartet as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- Added the four published `Pattern.sub` / `Pattern.subn` keyword rows on the existing `module_workflow_surface.py` owner path and extended the shared parity assertions to cover the resulting 87-row / 42-pattern-call frontier.
- Regenerated `reports/correctness/latest.py`; the tracked combined scorecard now reads `1457` total / `1457` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `87/87`, `module.workflow.str` at `56/56`, `module.workflow.bytes` at `31/31`, `module.workflow.pattern_call` at `42/42`, and `module.workflow.module_call` unchanged at `33/33`.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0783-module-workflow-pattern-sub-subn-keyword-quartet.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
