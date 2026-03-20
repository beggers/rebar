# RBR-0769: Publish the module-workflow module `split(maxsplit=__index__)` singleton

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the one remaining raw module keyword-argument singleton, publishing the literal `split(maxsplit=__index__)` workflow for the exact `b"abc"` / `b"zabcabcabc"` pair before module keyword error rows, pattern keyword rows, or another owner family reopen the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only one new `module_call` row:
  - add `workflow-module-split-maxsplit-indexlike-bytes`;
  - keep the row pinned to the exact direct parity anchor already defined on the shared owner path in `MODULE_KEYWORD_CALL_CASES`:
    - `module-split-maxsplit-indexlike-bytes`: `helper == "split"`, `args == [b"abc", b"zabcabcabc"]`, and `kwargs == {"maxsplit": _INDEX_TWO}`;
  - keep the new row on the `bytes` text model so the owner-path text-model split stays explicit; and
  - do not broaden into module keyword error rows, pattern keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `66` total rows instead of `65`;
  - update the shared `module_call` helper breakdown so the owner path now expects `5` `search` rows, `4` `match` rows, `4` `fullmatch` rows, `3` `split` rows, `1` `findall` row, `1` `finditer` row, `4` `sub` rows, `4` `subn` rows, and `2` `escape` rows;
  - extend the canonical published module-keyword slice by exactly one row so it now includes `workflow-module-split-maxsplit-indexlike-bytes` beside the existing `flags=`, `maxsplit=`, and replacement `count=` keyword rows;
  - keep the new row pinned to the exact direct anchor `module-split-maxsplit-indexlike-bytes` instead of inventing another keyword selector table or detached owner path; and
  - keep the published direct-case alignment honest by updating the canonical bytes subset assertions, selected direct-case sequence, and helper coverage checks without restoring mirrored sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1435` total / `1435` passed / `0` `unimplemented` across `114` manifests to `1436` / `1436` / `0` across the same `114` manifests;
  - `module.workflow` moves from `65` / `65` / `0` to `66` / `66` / `0`;
  - `module.workflow.str` stays `42` / `42` / `0`;
  - `module.workflow.bytes` moves from `23` / `23` / `0` to `24` / `24` / `0`;
  - `module.workflow.module_call` moves from `27` / `27` / `0` to `28` / `28` / `0`; and
  - the new singleton row is visible in the tracked scorecard as a representative `module-workflow-surface` module-call case.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0769-module-workflow-module-split-maxsplit-indexlike-singleton.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0769` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0768`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
- Queue this directly after `RBR-0767` on the same `module-workflow-surface` owner path so the raw module keyword ladder closes its remaining published singleton before module keyword error rows or pattern keyword rows reopen the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchor `module-split-maxsplit-indexlike-bytes` in `MODULE_KEYWORD_CALL_CASES`;
  - direct publication probes in this run confirmed `workflow-module-split-maxsplit-indexlike-bytes` is still absent from `tests/conformance/fixtures/module_workflow_surface.py`, the published module-keyword selector assertions in `tests/python/test_module_workflow_parity_suite.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_calls_match_cpython and module-split-maxsplit-indexlike-bytes'` passed in this run (`2 passed, 676 deselected`);
  - the current owner path already publishes the adjacent `workflow-module-split-maxsplit-keyword-bytes`, `workflow-module-sub-count-keyword-str`, `workflow-module-sub-count-indexlike-str`, `workflow-module-subn-count-keyword-bytes`, and `workflow-module-subn-count-indexlike-bytes` rows, leaving this singleton as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.
