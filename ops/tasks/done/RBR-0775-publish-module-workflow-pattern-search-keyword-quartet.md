# RBR-0775: Publish the module-workflow `Pattern.search` keyword quartet

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the remaining bounded `Pattern.search` keyword quartet, publishing the exact `endpos=` / `endpos=True` / `pos=__index__` / `endpos=__index__` workflows for the adjacent `"z"`, `"abc"`, and `b"abc"` anchors before the remaining `Pattern.match` / `Pattern.fullmatch` / `Pattern.findall` / `Pattern.finditer` bool-or-indexlike rows, pattern replacement keyword rows, compiled-pattern module keyword rows, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only four new `pattern_call` rows:
  - add `workflow-pattern-search-str-bool-endpos-keyword`;
  - add `workflow-pattern-search-bytes-endpos-keyword`;
  - add `workflow-pattern-search-str-pos-indexlike`;
  - add `workflow-pattern-search-bytes-endpos-indexlike`;
  - keep all four rows pinned to the exact direct parity anchors already defined on the shared owner path in `PATTERN_KEYWORD_CALL_CASES`:
    - `pattern-search-bool-endpos-keyword-str`: `helper == "search"`, `pattern == "z"`, `args == ("zabcabc",)`, and `kwargs == {"endpos": True}`;
    - `pattern-search-endpos-keyword-bytes`: `helper == "search"`, `pattern == b"abc"`, `args == (b"zabcabc",)`, and `kwargs == {"endpos": 4}`;
    - `pattern-search-pos-indexlike-str`: `helper == "search"`, `pattern == "abc"`, `args == ("zabcabc",)`, and `kwargs == {"pos": _INDEX_TWO}`;
    - `pattern-search-endpos-indexlike-bytes`: `helper == "search"`, `pattern == b"abc"`, `args == (b"zabcabc",)`, and `kwargs == {"endpos": _INDEX_FOUR}`;
  - keep the text-model split explicit: `workflow-pattern-search-str-bool-endpos-keyword` and `workflow-pattern-search-str-pos-indexlike` stay on `str`, while `workflow-pattern-search-bytes-endpos-keyword` and `workflow-pattern-search-bytes-endpos-indexlike` stay on `bytes`; and
  - do not broaden into the remaining `Pattern.match` / `Pattern.fullmatch` / `Pattern.findall` / `Pattern.finditer` bool-or-indexlike rows, `Pattern.split` / `Pattern.sub` / `Pattern.subn` keyword rows, module keyword rows, compiled-pattern module keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or detached selector table:
  - update the bundle-contract expectations so `module-workflow-surface` now publishes `75` total rows instead of `71`;
  - update the owner-path text-model split so the bundle now expects `49` `str` rows and `26` `bytes` rows;
  - update the shared `pattern_call` helper breakdown so the owner path now expects `14` `search` rows, `3` `match` rows, `9` `fullmatch` rows, `2` `findall` rows, and `2` `finditer` rows;
  - keep `module_call` expectations unchanged at `33` rows with the current helper breakdown;
  - extend `PUBLISHED_PATTERN_KEYWORD_PATTERN_CASES` by exactly these four rows so it now contains nine published pattern-keyword rows in this order:
    - `workflow-pattern-search-str-pos-keyword`
    - `workflow-pattern-search-str-bool-endpos-keyword`
    - `workflow-pattern-search-bytes-endpos-keyword`
    - `workflow-pattern-search-str-pos-indexlike`
    - `workflow-pattern-search-bytes-endpos-indexlike`
    - `workflow-pattern-match-str-pos-keyword`
    - `workflow-pattern-fullmatch-bytes-window-keyword`
    - `workflow-pattern-findall-str-window-keyword`
    - `workflow-pattern-finditer-bytes-window-keyword`
  - extend the focused direct-case alignment assertions so those nine published rows map back to these direct anchors in the same order:
    - `pattern-search-pos-keyword-str`
    - `pattern-search-bool-endpos-keyword-str`
    - `pattern-search-endpos-keyword-bytes`
    - `pattern-search-pos-indexlike-str`
    - `pattern-search-endpos-indexlike-bytes`
    - `pattern-match-pos-keyword-str`
    - `pattern-fullmatch-window-keyword-bytes`
    - `pattern-findall-window-keyword-str`
    - `pattern-finditer-window-keyword-bytes`
  - keep the published direct-case alignment honest without restoring mirrored sidecars or inventing another owner path.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1441` total / `1441` passed / `0` `unimplemented` across `114` manifests to `1445` / `1445` / `0` across the same `114` manifests;
  - `module.workflow` moves from `71` / `71` / `0` to `75` / `75` / `0`;
  - `module.workflow.str` moves from `47` / `47` / `0` to `49` / `49` / `0`;
  - `module.workflow.bytes` moves from `24` / `24` / `0` to `26` / `26` / `0`;
  - `module.workflow.pattern_call` moves from `26` / `26` / `0` to `30` / `30` / `0`;
  - `module.workflow.module_call` stays `33` / `33` / `0`; and
  - at least one of the new `workflow-pattern-search-*keyword*` rows is visible in the tracked scorecard as a representative `module-workflow-surface` pattern-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0775-module-workflow-pattern-search-keyword-quartet.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0775` is the next available task id in the current checkout:
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no `feature-implementation` task at the start of this run;
  - `ops/tasks/done/` currently runs through `RBR-0774`; and
  - the next-free-id probe across `ops/tasks/**` plus reserved ids in `ops/state/backlog.md` and `ops/state/current_status.md` returned `RBR-0775`.
- Queue this directly after `RBR-0773` on the same `module-workflow-surface` owner path so the first remaining `Pattern.search` keyword frontier lands before the adjacent `Pattern.match` / `Pattern.fullmatch` / `Pattern.findall` / `Pattern.finditer` bool-or-indexlike rows, pattern replacement keyword rows, compiled-pattern module keyword rows, or another owner family reopen the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `pattern-search-bool-endpos-keyword-str`, `pattern-search-endpos-keyword-bytes`, `pattern-search-pos-indexlike-str`, and `pattern-search-endpos-indexlike-bytes` in `PATTERN_KEYWORD_CALL_CASES`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'pattern_keyword_argument_calls_match_cpython and (pattern-search-endpos-keyword-bytes or pattern-search-bool-endpos-keyword-str or pattern-search-pos-indexlike-str or pattern-search-endpos-indexlike-bytes)'` passed in this run (`8 passed, 695 deselected`);
  - direct publication probes in this run confirmed the four new workflow ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the representative `workflow-pattern-search-str-pos-keyword` row but still stops short of the remaining `Pattern.search` `endpos=` / bool / `__index__` variants; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.

## Completion
- 2026-03-20: Added exactly four new `pattern_call` rows to `tests/conformance/fixtures/module_workflow_surface.py`: `workflow-pattern-search-str-bool-endpos-keyword`, `workflow-pattern-search-bytes-endpos-keyword`, `workflow-pattern-search-str-pos-indexlike`, and `workflow-pattern-search-bytes-endpos-indexlike`. The rows stay on the existing `module-workflow-surface` owner manifest, preserve the required `str`/`bytes` split, and reuse the exact direct anchors already defined in `PATTERN_KEYWORD_CALL_CASES`, including `_INDEX_TWO` and `_INDEX_FOUR` for the `__index__` cases.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the owner-path contract now expects `75` published rows, a `49`/`26` `str`/`bytes` split, and `30` published `pattern_call` rows with a `14`/`3`/`9`/`2`/`2` `search`/`match`/`fullmatch`/`findall`/`finditer` helper breakdown. The published pattern-keyword slice now contains nine rows in the required order and maps back to the nine direct anchors in that same order, using normalized keyword signatures so the new `__index__` rows compare by value rather than object identity.
- Extended `tests/conformance/test_combined_correctness_scorecards.py` to include the newly published `Pattern.search` keyword slice in the `module-workflow-surface` representative inventory, then republished `reports/correctness/latest.py`. Reading the tracked artifact shows `1445` total / `1445` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `75/75/0`, `module.workflow.str` at `49/49/0`, `module.workflow.bytes` at `26/26/0`, `module.workflow.pattern_call` at `30/30/0`, and `module.workflow.module_call` unchanged at `33/33/0`. The tracked report now includes `workflow-pattern-search-str-bool-endpos-keyword` as a visible representative `module-workflow-surface` pattern-call case.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0775-module-workflow-pattern-search-keyword-quartet.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`, and `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`. No existing benchmark workload or benchmark expectation module matched these four exact keyword rows, so this run stayed on the required correctness-publication path only.
