# RBR-0779: Publish the module-workflow `Pattern.findall` / `Pattern.finditer` keyword quartet

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent pattern-keyword quartet, publishing the exact `Pattern.findall(pos=__index__, endpos=__index__)`, `Pattern.findall(pos=True, endpos=7)`, `Pattern.finditer(pos=__index__, endpos=__index__)`, and `Pattern.finditer(pos=True, endpos=7)` workflows for the existing `"abc"` and `b"abc"` anchors before the remaining pattern `split` / `sub` / `subn` keyword rows, compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only four new `pattern_call` rows:
  - add `workflow-pattern-findall-str-window-indexlike`;
  - add `workflow-pattern-findall-str-bool-window-keyword`;
  - add `workflow-pattern-finditer-bytes-window-indexlike`;
  - add `workflow-pattern-finditer-bytes-bool-window-keyword`;
  - keep all four rows pinned to the exact direct parity anchors already defined on the shared owner path in `PATTERN_KEYWORD_CALL_CASES`:
    - `pattern-findall-window-indexlike-str`: `helper == "findall"`, `pattern == "abc"`, `args == ("zabcabcabcz",)`, and `kwargs == {"pos": _INDEX_ONE, "endpos": _INDEX_SEVEN}`;
    - `pattern-findall-bool-window-keyword-str`: `helper == "findall"`, `pattern == "abc"`, `args == ("zabcabcz",)`, and `kwargs == {"pos": True, "endpos": 7}`;
    - `pattern-finditer-window-indexlike-bytes`: `helper == "finditer"`, `pattern == b"abc"`, `args == (b"zabcabcabcz",)`, and `kwargs == {"pos": _INDEX_ONE, "endpos": _INDEX_SEVEN}`;
    - `pattern-finditer-bool-window-keyword-bytes`: `helper == "finditer"`, `pattern == b"abc"`, `args == (b"zabcabcz",)`, and `kwargs == {"pos": True, "endpos": 7}`;
  - keep the text-model split explicit: both `workflow-pattern-findall-*` rows stay on `str`, while both `workflow-pattern-finditer-*` rows stay on `bytes`; and
  - do not broaden into the remaining pattern `split` / `sub` / `subn` keyword rows, module keyword rows, compiled-pattern module keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `81` total rows instead of `77`;
  - update the owner-path text-model split so the bundle now expects `52` `str` rows and `29` `bytes` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `14` `search` rows, `4` `match` rows, `10` `fullmatch` rows, `4` `findall` rows, and `4` `finditer` rows;
  - keep `module_call` expectations unchanged at `33` rows with the current helper breakdown;
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly these four rows so it now contains fifteen published pattern-keyword rows in this order:
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
  - extend the focused direct-case alignment assertions so those fifteen published rows map back to these direct anchors in the same order:
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
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1447` total / `1447` passed / `0` `unimplemented` across `114` manifests to `1451` / `1451` / `0` across the same `114` manifests;
  - `module.workflow` moves from `77` / `77` / `0` to `81` / `81` / `0`;
  - `module.workflow.str` moves from `50` / `50` / `0` to `52` / `52` / `0`;
  - `module.workflow.bytes` moves from `27` / `27` / `0` to `29` / `29` / `0`;
  - `module.workflow.pattern_call` moves from `32` / `32` / `0` to `36` / `36` / `0`;
  - `module.workflow.module_call` stays `33` / `33` / `0`; and
  - at least one of the new `workflow-pattern-findall-*` or `workflow-pattern-finditer-*` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0779-module-workflow-pattern-findall-finditer-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0779` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0778`; and
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run.
- Queue this directly after `RBR-0777` on the same `module-workflow-surface` owner path so the remaining adjacent `Pattern.findall` / `Pattern.finditer` keyword-window quartet lands before the pattern `split` / `sub` / `subn` keyword rows, compiled-pattern module keyword rows, benchmark catch-up, or another owner family reopens the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-findall-window-indexlike-str`, `pattern-findall-bool-window-keyword-str`, `pattern-finditer-window-indexlike-bytes`, and `pattern-finditer-bool-window-keyword-bytes` in `PATTERN_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword_argument_calls_match_cpython and (pattern-findall-window-indexlike-str or pattern-findall-bool-window-keyword-str or pattern-finditer-window-indexlike-bytes or pattern-finditer-bool-window-keyword-bytes)'` passed in this run (`8 passed, 707 deselected`);
  - direct publication probes in this run confirmed the four new workflow ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - the current owner path already publishes the adjacent `Pattern.findall(pos=..., endpos=...)` and `Pattern.finditer(pos=..., endpos=...)` representative rows, leaving this bool-plus-`__index__` quartet as the smallest unpublished neighbor on the same owner file; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- Added the four adjacent `module-workflow-surface` pattern-keyword rows on the existing owner path: `workflow-pattern-findall-str-window-indexlike`, `workflow-pattern-findall-str-bool-window-keyword`, `workflow-pattern-finditer-bytes-window-indexlike`, and `workflow-pattern-finditer-bytes-bool-window-keyword`.
- Updated the shared parity-suite publication counts and alignment assertions to `81` owner-path cases, `52` `str` rows, `29` `bytes` rows, and `36` published `pattern_call` rows while keeping `module_call` at `33`.
- Regenerated the tracked published correctness scorecard at `reports/correctness/latest.py`; the tracked artifact now reports `1451` total / `1451` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `81/81/0`, `module.workflow.str` at `52/52/0`, `module.workflow.bytes` at `29/29/0`, `module.workflow.pattern_call` at `36/36/0`, and `module.workflow.module_call` unchanged at `33/33/0`. The tracked report includes the new representative case `workflow-pattern-findall-str-window-indexlike`.
- Verified with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0779-module-workflow-pattern-findall-finditer-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`
