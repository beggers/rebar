# RBR-0763: Publish the module-workflow module keyword fullmatch/split pair

Status: ready
Owner: feature-implementation
Created: 2026-03-20

## Goal
- Reopen the existing `module-workflow-surface` correctness frontier with the next adjacent module keyword-argument pair, so the shared owner path keeps widening through the already-landed direct parity anchors before the remaining index-like keyword variants, replacement count keywords, keyword error cases, pattern keyword rows, or another owner family reopen the queue.

## Deliverables
- `tests/conformance/fixtures/module_workflow_surface.py`
- `tests/python/test_module_workflow_parity_suite.py`
- `tests/conformance/test_combined_correctness_scorecards.py`
- `reports/correctness/latest.py`

## Acceptance Criteria
- `tests/conformance/fixtures/module_workflow_surface.py` remains the only correctness manifest for this slice and grows by only two new `module_call` rows:
  - add `workflow-module-fullmatch-flags-keyword-str` and `workflow-module-split-maxsplit-keyword-bytes`;
  - keep both rows pinned to the exact adjacent direct parity anchors already defined on the shared owner path in `MODULE_KEYWORD_CALL_CASES`:
    - `module-fullmatch-flags-keyword-str`: `helper == "fullmatch"`, `args == ["abc", "Abc"]`, and `kwargs == {"flags": 2}`;
    - `module-split-maxsplit-keyword-bytes`: `helper == "split"`, `args == [b"abc", b"zabczabc"]`, and `kwargs == {"maxsplit": 1}`;
  - keep `workflow-module-fullmatch-flags-keyword-str` on the `str` text model and `workflow-module-split-maxsplit-keyword-bytes` on the `bytes` text model so the owner-path text-model split stays explicit; and
  - do not broaden into the remaining module keyword index-like variants, `sub()` / `subn()` count keywords, keyword error rows, pattern keyword rows, benchmarks, native-boundary scaffolding, or any new manifest in this run.
- `tests/python/test_module_workflow_parity_suite.py` keeps this work on the existing shared owner path without another keyword-only manifest or suite:
  - update the bundle-contract expectations, selected case-id inventory, and operation/helper counts so `module-workflow-surface` now publishes `56` total rows instead of `54`;
  - update the shared `module_call` helper breakdown so the owner path now expects `5` `search` rows, `4` `match` rows, `4` `fullmatch` rows, `2` `split` rows, `1` `findall` row, `1` `finditer` row, `2` `sub` rows, `2` `subn` rows, and `2` `escape` rows;
  - extend the canonical published module-call slice by exactly two rows so it now includes `workflow-module-fullmatch-flags-keyword-str` and `workflow-module-split-maxsplit-keyword-bytes` beside the existing bounded-wildcard, compiled-pattern helper, replacement-helper mismatch, `escape()`, and first module keyword rows;
  - keep the new rows pinned to the exact direct anchors `module-fullmatch-flags-keyword-str` and `module-split-maxsplit-keyword-bytes` instead of inventing another keyword selector table or detached owner path; and
  - keep the published direct-case alignment honest by updating the canonical selected direct-case sequence, text-model subset assertions, and module-helper coverage checks without restoring mirrored sidecars.
- `tests/conformance/test_combined_correctness_scorecards.py` and `reports/correctness/latest.py` are regenerated honestly:
  - the combined report moves from `1424` total / `1424` passed / `0` `unimplemented` across `114` manifests to `1426` / `1426` / `0` across the same `114` manifests;
  - `module.workflow` moves from `54` / `54` / `0` to `56` / `56` / `0`;
  - `module.workflow.str` moves from `36` / `36` / `0` to `37` / `37` / `0`;
  - `module.workflow.bytes` moves from `18` / `18` / `0` to `19` / `19` / `0`;
  - `module.workflow.module_call` moves from `21` / `21` / `0` to `23` / `23` / `0`; and
  - both new module keyword rows are visible in the tracked scorecard as representative `module-workflow-surface` module-call cases.
- Verification passes with:
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py tests/conformance/test_combined_correctness_scorecards.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --fixtures tests/conformance/fixtures/module_workflow_surface.py --report .rebar/tmp/rbr-0763-module-workflow-module-keyword-fullmatch-split-pair.py`
  - `PYTHONPATH=python ./.venv/bin/python -m rebar_harness.correctness --report reports/correctness/latest.py`

## Constraints
- Keep this task correctness-publication only. Do not change Rust implementation files, `python/rebar/__init__.py`, benchmark manifests, benchmark reports, README text, or harness files outside the existing correctness publication path in this run.
- Reuse the existing `module_workflow_surface.py` manifest and `tests/python/test_module_workflow_parity_suite.py` owner path. Do not create another correctness manifest, another parity suite, or a detached keyword-argument publication file.

## Notes
- `RBR-0763` is the next available task id in the current checkout:
  - `ops/tasks/done/` currently runs through `RBR-0762`;
  - `ops/tasks/ready/`, `ops/tasks/in_progress/`, and `ops/tasks/blocked/` had no newer `feature-implementation` task at the start of this run; and
  - `ops/state/backlog.md` and the frontier prose in `ops/state/current_status.md` already honestly say that no ready feature follow-on currently survives after the likely same-cycle drain, so this one-task refill does not need a backlog-frontier prose change.
- Queue this directly after `RBR-0761` on the same `module-workflow-surface` owner path so the published module keyword ladder stays adjacent: finish the remaining `flags=` `fullmatch()` row and the first `maxsplit=` `split()` row before the index-like keyword variants, replacement count keywords, or keyword error cases reopen the queue.
- 2026-03-20 feature-planning probes confirm this follow-on is concrete from the landed frontier:
  - `tests/python/test_module_workflow_parity_suite.py` already carries the exact adjacent direct parity anchors `module-fullmatch-flags-keyword-str` and `module-split-maxsplit-keyword-bytes` in `MODULE_KEYWORD_CALL_CASES`;
  - direct runtime probes in this run confirmed that `rebar.fullmatch("abc", "Abc", flags=int(re.IGNORECASE))` and `rebar.split(b"abc", b"zabczabc", maxsplit=1)` match CPython exactly;
  - `PYTHONPATH=python ./.venv/bin/python -m pytest -q tests/python/test_module_workflow_parity_suite.py -k 'module_keyword_argument_calls_match_cpython and (module-fullmatch-flags-keyword-str or module-split-maxsplit-keyword-bytes)'` passed in this run (`4 passed, 655 deselected`);
  - `tests/conformance/fixtures/module_workflow_surface.py` currently publishes the first module keyword `search()` / `match()` pair but not this adjacent `fullmatch()` / `split()` pair, leaving these two rows as the next bounded publication on the same owner path; and
  - no blocked feature task exists to reopen first.
