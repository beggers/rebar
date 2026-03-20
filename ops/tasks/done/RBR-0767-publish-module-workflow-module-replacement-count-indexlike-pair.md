# RBR-0767: Publish the module-workflow module replacement count index-like pair

Status: done
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent raw module keyword-argument pair, publishing the literal replacement `count=__index__` workflows for the exact `"abc"` / `b"abc"` pattern pair before the remaining `split(..., maxsplit=__index__)` singleton, module keyword error rows, or another owner family reopens the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-sub-count-indexlike-str` and `workflow-module-subn-count-indexlike-bytes`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `MODULE_KEYWORD_CALL_CASES`:
    - `module-sub-count-indexlike-str`: `helper == "sub"`, `args == ["abc", "x", "abcabcabc"]`, and `kwargs == {"count": _INDEX_TWO}`;
    - `module-subn-count-indexlike-bytes`: `helper == "subn"`, `args == [b"abc", b"x", b"abcabcabc"]`, and `kwargs == {"count": _INDEX_TWO}`;
  - keep `workflow-module-sub-count-indexlike-str` on the `str` text model and `workflow-module-subn-count-indexlike-bytes` on the `bytes` text model so the owner-path text-model split stays explicit; and
  - do not broaden into `workflow-module-split-maxsplit-indexlike-bytes`, module keyword error rows, pattern keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `65` total rows instead of `63`;
  - update the shared `module_call` helper breakdown so the owner path now expects `5` `search` rows, `4` `match` rows, `4` `fullmatch` rows, `2` `split` rows, `1` `findall` row, `1` `finditer` row, `4` `sub` rows, `4` `subn` rows, and `2` `escape` rows;
  - extend the canonical published module-call slice by exactly two rows so it now includes `workflow-module-sub-count-indexlike-str` and `workflow-module-subn-count-indexlike-bytes` beside the existing bounded-wildcard, compiled-pattern helper, replacement-helper mismatch, `escape()`, and plain module keyword rows;
  - keep the new rows pinned to the exact direct anchors `module-sub-count-indexlike-str` and `module-subn-count-indexlike-bytes` instead of inventing another keyword selector table or detached owner path; and
  - keep the published direct-case alignment honest by updating the canonical selected direct-case sequence, text-model subset assertions, and module-helper coverage checks without restoring mirrored sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1433` total / `1433` passed / `0` `unimplemented` across `114` manifests to `1435` / `1435` / `0` across the same `114` manifests;
  - `module.workflow` moves from `63` / `63` / `0` to `65` / `65` / `0`;
  - `module.workflow.str` moves from `41` / `41` / `0` to `42` / `42` / `0`;
  - `module.workflow.bytes` moves from `22` / `22` / `0` to `23` / `23` / `0`;
  - `module.workflow.module_call` moves from `25` / `25` / `0` to `27` / `27` / `0`; and
  - both new module keyword rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0767-module-workflow-module-replacement-count-indexlike-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0767` is the next available task id in the current checkout:
  - queue inspection at the start of this run found no ready, in-progress, or blocked tasks; and
  - the next-free-id probe across `ops/tasks/**` plus reserved ids in `ops/state/backlog.md` and `ops/state/current_status.md` returned `RBR-0767`.
- Queue this directly after `RBR-0765` on the same `module-workflow-surface` owner path so the raw module replacement keyword ladder stays adjacent: land the `count=__index__` replacement pair before the remaining raw `maxsplit=__index__` singleton or module keyword error rows reopen the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-sub-count-indexlike-str` and `module-subn-count-indexlike-bytes` in `MODULE_KEYWORD_CALL_CASES`;
  - direct publication probes in this run confirmed the workflow ids are still absent from `tests/conformance/fixtures/module_workflow_surface.py`, `tests/conformance/test_combined_correctness_scorecards.py`, and `reports/correctness/latest.py`;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_calls_match_cpython and (module-sub-count-indexlike-str or module-subn-count-indexlike-bytes)'` passed in this run (`4 passed, 674 deselected`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the adjacent plain replacement `count=` rows but not this `__index__` pair, leaving these two rows as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.

## Completion Note
- Published `workflow-module-sub-count-indexlike-str` and `workflow-module-subn-count-indexlike-bytes` on the existing `module-workflow-surface` manifest using fixture-local `__index__` carriers so the correctness publication can serialize the new kwargs without widening into another manifest or harness edit.
- Updated `tests/python/test_module_workflow_parity_suite.py` so the shared owner path now expects `65` published rows, `42` `str` rows, `23` `bytes` rows, and `27` `module_call` rows with `4` `sub` and `4` `subn` helpers; the module-keyword selector still maps to the existing direct anchors, now through a semantic `__index__` kwargs signature instead of object identity.
- Regenerated `reports/correctness/latest.py`; the tracked publication now reports `1435` total / `1435` passed / `0` unimplemented across `114` manifests, with `module.workflow` at `65` / `65` / `0`, `module.workflow.str` at `42` / `42` / `0`, `module.workflow.bytes` at `23` / `23` / `0`, and `module.workflow.module_call` at `27` / `27` / `0`. The tracked report includes both new case ids.
- Verified with `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`, `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0767-module-workflow-module-replacement-count-indexlike-pair.py`, and `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`.
