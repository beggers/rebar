# RBR-0765: Publish the module-workflow module replacement count keyword pair

Status: done
Owner: feature-implementation
Created: 2026-03-20
Completed: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent raw module keyword-argument pair, so the shared owner path lands the plain module-level replacement `count=` workflows before the remaining index-like keyword variants, module keyword error rows, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-sub-count-keyword-str` and `workflow-module-subn-count-keyword-bytes`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `MODULE_KEYWORD_CALL_CASES`:
    - `module-sub-count-keyword-str`: `helper == "sub"`, `args == ["abc", "x", "abcabc"]`, and `kwargs == {"count": 1}`;
    - `module-subn-count-keyword-bytes`: `helper == "subn"`, `args == [b"abc", b"x", b"abcabc"]`, and `kwargs == {"count": 1}`;
  - keep `workflow-module-sub-count-keyword-str` on the `str` text model and `workflow-module-subn-count-keyword-bytes` on the `bytes` text model so the owner-path text-model split stays explicit; and
  - do not broaden into the index-like `count=` variants, module keyword error rows, pattern keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `63` total rows instead of `61`;
  - update the shared `module_call` helper breakdown so the owner path now expects `5` `search` rows, `4` `match` rows, `4` `fullmatch` rows, `2` `split` rows, `1` `findall` row, `1` `finditer` row, `3` `sub` rows, `3` `subn` rows, and `2` `escape` rows;
  - extend the canonical published module-call slice by exactly two rows so it now includes `workflow-module-sub-count-keyword-str` and `workflow-module-subn-count-keyword-bytes` beside the existing bounded-wildcard, compiled-pattern helper, replacement-helper mismatch, `escape()`, and first module keyword rows;
  - keep the new rows pinned to the exact direct anchors `module-sub-count-keyword-str` and `module-subn-count-keyword-bytes` instead of inventing another keyword selector table or detached owner path; and
  - keep the published direct-case alignment honest by updating the canonical selected direct-case sequence, text-model subset assertions, and module-helper coverage checks without restoring mirrored sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1431` total / `1431` passed / `0` `unimplemented` across `114` manifests to `1433` / `1433` / `0` across the same `114` manifests;
  - `module.workflow` moves from `61` / `61` / `0` to `63` / `63` / `0`;
  - `module.workflow.str` moves from `40` / `40` / `0` to `41` / `41` / `0`;
  - `module.workflow.bytes` moves from `21` / `21` / `0` to `22` / `22` / `0`;
  - `module.workflow.module_call` moves from `23` / `23` / `0` to `25` / `25` / `0`; and
  - both new module keyword rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0765-module-workflow-module-replacement-count-keyword-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0765` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0764`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
- Queue this directly after `RBR-0763` on the same `module-workflow-surface` owner path so the raw module keyword ladder stays adjacent: land the plain `count=` replacement pair before the index-like `count=` variants or module keyword error rows reopen the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-sub-count-keyword-str` and `module-subn-count-keyword-bytes` in `MODULE_KEYWORD_CALL_CASES`;
  - direct runtime probes in this run confirmed that `rebar.sub("abc", "x", "abcabc", count=1)` and `rebar.subn(b"abc", b"x", b"abcabc", count=1)` match CPython exactly;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_calls_match_cpython and (module-sub-count-keyword-str or module-subn-count-keyword-bytes)'` passed in this run (`4 passed, 662 deselected`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the earlier module keyword `flags=` and `maxsplit=` rows but not this adjacent plain replacement `count=` pair, leaving these two rows as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion
- 2026-03-20: Published `workflow-module-sub-count-keyword-str` and `workflow-module-subn-count-keyword-bytes` on the existing `module-workflow-surface` manifest, keeping both rows pinned to the existing `MODULE_KEYWORD_CALL_CASES` anchors on the shared parity owner path.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the canonical owner bundle now asserts `63` published module-workflow rows, a `41`/`22` `str`/`bytes` split, a `25`-row `module_call` surface, and the widened module keyword helper breakdown while mapping the published keyword rows back to `module-sub-count-keyword-str` and `module-subn-count-keyword-bytes`.
- Updated the representative `module-workflow-surface` sample set in `tests/conformance/test_combined_correctness_scorecards.py` and republished `reports/correctness/latest.py`; the tracked combined scorecard now reports `1433` total / `1433` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `63`/`63`/`0`, `module.workflow.str` at `41`/`41`/`0`, `module.workflow.bytes` at `22`/`22`/`0`, and `module.workflow.module_call` at `25`/`25`/`0`.
- Verification passed with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py` (`690 passed, 1 skipped, 1940 subtests passed in 35.33s`), `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0765-module-workflow-module-replacement-count-keyword-pair.py` (`63` executed / `63` passed), and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py` (`1433` executed / `1433` passed).
